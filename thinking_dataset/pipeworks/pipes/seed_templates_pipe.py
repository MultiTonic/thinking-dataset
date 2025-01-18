# @file thinking_dataset/pipeworks/pipes/seed_templates_pipe.py
# @description Pipe for seeding templates with specific values using database.
# @version 1.6.16
# @license MIT

import json, random, re, pandas as pd  # noqa
from tqdm import tqdm
from .pipe import Pipe
from typing import List, Dict
from thinking_dataset.utils.log import Log
from sqlalchemy import select, Table, MetaData
from thinking_dataset.db.database import Database
from tenacity import retry, stop_after_attempt, wait_fixed


class SeedTemplatesPipe(Pipe):

    def _get_seeds(self, seeds: pd.DataFrame, amount: int, size: int,
                   offset: int) -> List[str]:
        seed_texts = []
        count = len(seeds)
        if count == 0:
            raise ValueError("No seeds available to generate.")
        for _ in range(amount):
            index = random.randint(0, count - 1)
            seed = seeds.iloc[index].values[0]
            trimmed = seed[offset:offset + size]
            seed_texts.append(trimmed)
        return seed_texts

    def _get_query(self, template: str, seeds: List[str]) -> str:
        seeds_str = ', '.join(json.dumps(seed) for seed in seeds)
        query = re.sub(r'"{{\s*seeds\s*}}"', f'{seeds_str}', template)
        return query

    def _validate(self, df: pd.DataFrame, column: str):
        if column not in df.columns or df[column].iloc[0] is None:
            raise ValueError(f"DataFrame '{column}' column is invalid")

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2), reraise=True)
    def _write_to_db(self, df: pd.DataFrame, session, out_table: str,
                     if_exists: str):
        df.to_sql(out_table, session.bind, if_exists=if_exists, index=False)
        Log.info(f"Inserted {len(df)} rows into '{out_table}' table")

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
        size = config["seed_length"]
        offset = config["seed_offset"]

        table = Table(table_name, MetaData(), autoload_with=session.bind)
        seeds = pd.read_sql(select(table.c[in_column]), session.bind)
        count = len(seeds)
        query = "template"
        Log.info(f"Total seeds in {table_name}.{in_column}: {count}")

        self._validate(df, query)
        queries = [
            self._get_query(df[query].iloc[0],
                            self._get_seeds(seeds, amount, size, offset))
            for _ in tqdm(range(batch_size),
                          desc="Generating Queries",
                          total=batch_size,
                          unit="q")
        ]

        df = pd.DataFrame({
            "id": range(1, batch_size + 1),
            out_column: queries
        })

        self._write_to_db(df, session, out_table, if_exists)
        return df

    def flow(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        Log.info("Starting SeedTemplatesPipe")
        with Database().get_session() as session:
            df = self._process(session, self.config, df)
        Log.info("Finished SeedTemplatesPipe")
        return df
