# @file thinking_dataset/pipeworks/pipes/response_generation_pipe.py
# @description Pipe for generating responses from inspirations.
# @version 1.0.22
# @license MIT

import asyncio
import pandas as pd
from .pipe import Pipe
from thinking_dataset.utils.log import Log
from sqlalchemy import select, Table, MetaData, update, DDL, event
from tenacity import retry, stop_after_attempt, wait_fixed
from thinking_dataset.providers.ollama_provider import OllamaProvider
from thinking_dataset.decorators.with_db_session import with_db_session


class ResponseGenerationPipe(Pipe):

    async def _generate_response(self, query: str,
                                 provider: OllamaProvider) -> str:
        response = await provider.process_request_async(prompt=query)
        return response

    def _fetch_queries(self, session, table_name: str,
                       in_column: str) -> pd.DataFrame:
        table = Table(table_name, MetaData(), autoload_with=session.bind)

        # Include id column in select
        query = select(table.c.id, table.c[in_column])
        result = session.execute(query)
        rows = result.fetchall()

        # Include both id and content columns
        queries = pd.DataFrame(rows, columns=['id', in_column])
        Log.info(f"Total Queries in {table_name}.{in_column}: {len(queries)}")
        return queries

    async def _ensure_column_exists(self, session, table, out_column):
        if out_column not in table.columns:
            Log.info(f"Column '{out_column}' does not exist "
                     f"in table '{table.name}', adding it.")

            # Use SQLAlchemy's DDL construct to add the column
            ddl = DDL(f'ALTER TABLE {table.name} ADD COLUMN {out_column} TEXT')
            event.listen(table, 'after_create',
                         ddl.execute_if(dialect='sqlite'))
            session.execute(ddl)

            # Reflect the table again to include the new column
            table = Table(table.name, MetaData(), autoload_with=session.bind)
        return table

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2), reraise=True)
    async def _update_db(self, session, out_table: str, row_id: int,
                         response: str, out_column: str):
        table = Table(out_table, MetaData(), autoload_with=session.bind)
        Log.info(
            f"Updating table '{out_table}' for row id {row_id} with column "
            f"'{out_column}'")
        Log.info(f"Response: {response}")
        Log.info(f"Table columns: {[col.name for col in table.columns]}")

        table = await self._ensure_column_exists(session, table, out_column)

        stmt = update(table).where(table.c.id == row_id).values(
            {out_column: response})
        session.execute(stmt)
        session.commit()
        Log.info(f"Updated row with id {row_id} in '{out_table}' table")

    async def _process_queries(self, session, queries, provider, out_table,
                               out_column, in_column):
        tasks = []
        for _, row in queries.iterrows():
            task = asyncio.create_task(
                self._process_single_query(session, row, provider, out_table,
                                           out_column, in_column))
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def _process_single_query(self, session, row, provider, out_table,
                                    out_column, in_column):
        response = await self._generate_response(row[in_column], provider)
        await self._update_db(session, out_table, row['id'], response,
                              out_column)

    @with_db_session
    def flow(self, df: pd.DataFrame, session=None, **kwargs) -> pd.DataFrame:
        Log.info("Starting ResponseGenerationPipe")

        in_config = self.config["input"][0]
        out_config = self.config["output"][0]
        in_table = in_config["table"]
        in_column = in_config["columns"][0]
        out_table = out_config["table"]
        out_column = out_config["columns"][0]

        async def process():
            try:
                queries = self._fetch_queries(session, in_table, in_column)
                provider = OllamaProvider.initialize(self.config)
                await self._process_queries(session, queries, provider,
                                            out_table, out_column, in_column)
            except Exception as e:
                session.rollback()
                raise e

        asyncio.run(process())
        Log.info("Finished ResponseGenerationPipe")
        return df
