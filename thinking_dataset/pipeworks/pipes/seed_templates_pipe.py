# @file thinking_dataset/pipeworks/pipes/seed_templates_pipe.py
# @description Pipe for seeding templates with specific values using database.
# @version 1.6.10
# @license MIT

import json, random, re, pandas as pd  # noqa
from sqlalchemy import select, Table, MetaData
from typing import List, Dict
from tqdm import tqdm
from .pipe import Pipe
from thinking_dataset.utils.log import Log
from thinking_dataset.db.database import Database


class SeedTemplatesPipe(Pipe):

    def _get_seeds(self, df: pd.DataFrame, amount: int,
                   count: int) -> List[str]:
        return [
            df.iloc[random.randint(0, count - 1)].values[0]
            for _ in range(amount)
        ]

    def _get_query(self, template: str, seeds: List[str]) -> str:
        return re.sub(r'\{\{\s*seeds\s*\}\}', json.dumps(seeds), template)

    def _validate(self, df: pd.DataFrame, column: str):
        if column not in df.columns or df[column].iloc[0] is None:
            raise ValueError(f"DataFrame '{column}' column is invalid")

    def _process(self, session, config: Dict[str, any],
                 df: pd.DataFrame) -> pd.DataFrame:
        in_config = config["input"][0]
        out_config = config["output"][0]
        table_name = in_config["table"]
        in_column = in_config["columns"][0]
        out_column = out_config["columns"][0]
        out_table = out_config["table"]
        batch_size = config["batch_size"]
        if_exists = config["if_exists"]
        amount = config["seed_amount"]

        table = Table(table_name, MetaData(), autoload_with=session.bind)
        seeds = pd.read_sql(select(table.c[in_column]), session.bind)
        count = len(seeds)
        query = "template"
        Log.info(f"Total seeds in {table_name}.{in_column}: {count}")

        self._validate(df, query)
        queries = [
            self._get_query(df[query].iloc[0],
                            self._get_seeds(seeds, amount, count))
            for _ in tqdm(range(batch_size),
                          desc="Generating Queries...",
                          total=batch_size,
                          unit="Q")
        ]

        df = pd.DataFrame({
            "id": range(1, batch_size + 1),
            out_column: queries
        })

        df.to_sql(out_table, session.bind, if_exists=if_exists, index=False)

        Log.info(f"Inserted {len(queries)} rows into '{out_table}' table")
        return df

    def flow(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        Log.info("Starting SeedTemplatesPipe")
        with Database().get_session() as session:
            df = self._process(session, self.config, df)
        Log.info("Finished SeedTemplatesPipe")
        return df
