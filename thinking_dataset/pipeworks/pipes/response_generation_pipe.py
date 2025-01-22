# @file thinking_dataset/pipeworks/pipes/response_generation_pipe.py
# @description Pipe for generating responses from inspirations.
# @version 1.0.16
# @license MIT

import asyncio
import pandas as pd
from typing import Dict
from .pipe import Pipe
from thinking_dataset.utils.log import Log
from thinking_dataset.db.database import Database
from sqlalchemy import select, Table, MetaData, update
from tenacity import retry, stop_after_attempt, wait_fixed
from thinking_dataset.providers.ollama_provider import OllamaProvider


class ResponseGenerationPipe(Pipe):

    async def _generate_response(self, query: str,
                                 provider: OllamaProvider) -> str:
        response = await provider.process_request_async(prompt=query)
        print(f"|Q|{query}|")
        print(f"|R|{response}|")
        return response

    def _fetch_queries(self, session, table_name: str,
                       in_column: str) -> pd.DataFrame:
        table = Table(table_name, MetaData(), autoload_with=session.bind)
        queries = pd.read_sql(select(table.c[in_column]), session.bind)
        Log.info(f"Total Queries in {table_name}.{in_column}: {len(queries)}")
        return queries

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2), reraise=True)
    async def _update_db(self, session, out_table: str, row_id: int,
                         response: str, out_column: str):
        table = Table(out_table, MetaData(), autoload_with=session.bind)
        stmt = update(table).where(table.c.id == row_id).values(
            {out_column: response})
        session.execute(stmt)
        session.commit()
        Log.info(f"Updated row with id {row_id} in '{out_table}' table")

    async def _process(self, session, config: Dict[str, any],
                       df: pd.DataFrame):
        in_config = config["input"][0]
        out_config = config["output"][0]
        in_table = in_config["table"]
        in_column = in_config["columns"][0]
        out_table = out_config["table"]
        out_column = out_config["columns"][0]

        queries = self._fetch_queries(session, in_table, in_column)
        provider = OllamaProvider.initialize(config)

        for _, row in queries.iterrows():
            response = await self._generate_response(row[in_column], provider)
            await self._update_db(session, out_table, row['id'], response,
                                  out_column)

    def flow(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        Log.info("Starting ResponseGenerationPipe")
        with Database().get_session() as session:
            asyncio.run(self._process(session, self.config, df))
        Log.info("Finished ResponseGenerationPipe")
        return df
