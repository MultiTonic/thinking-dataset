# @file thinking_dataset/pipeworks/pipes/query_generation_pipe.py
# @description Pipe for generating queries from templates and seeds.
# @version 1.1.26
# @license MIT

import re
import random
import pandas as pd
from tqdm import tqdm
from .pipe import Pipe
from typing import List
from thinking_dataset.utils.log import Log
from sqlalchemy import select, Table, MetaData
from tenacity import retry, stop_after_attempt, wait_fixed
from thinking_dataset.templates.template_loader import TemplateLoader
from thinking_dataset.decorators.with_db_session import with_db_session


class QueryGenerationPipe(Pipe):

    def _get_seeds(self, seeds: pd.DataFrame, amount: int, size: int,
                   offset: int) -> List[str]:
        seeds_length = len(seeds)
        if seeds_length == 0:
            raise ValueError("No seeds available to generate.")
        indices = random.sample(range(seeds_length), amount)
        seed_texts = []
        for idx in indices:
            seed = seeds.iloc[idx].values[0][offset:offset + size]
            seed_texts.append(seed)
        return seed_texts

    def _get_query(self, template: str, seeds: List[str]) -> str:
        value = '\n' + '\n'.join(f'{seed}\n' for seed in seeds)
        return re.sub(r'{{\s*seeds\s*}}', value, template)

    def _validate(self, df: pd.DataFrame, column: str):
        if df.empty:
            raise ValueError("DataFrame is empty.")
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")
        if df[column].isnull().all():
            raise ValueError(f"All values in column '{column}' are null.")

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2), reraise=True)
    def _write_to_db(self, df: pd.DataFrame, session, out_table: str,
                     if_exists: str):
        df.to_sql(out_table, session.bind, if_exists=if_exists, index=False)
        Log.info(f"Inserted {len(df)} rows into '{out_table}' table")

    def _generate_queries(self, seeds_df: pd.DataFrame, seed_amount: int,
                          size: int, offset: int, template: str,
                          batch_size: int) -> List[str]:
        queries = []
        for _ in tqdm(range(batch_size), desc="Generating Queries", unit="qu"):
            seeds = self._get_seeds(seeds_df, seed_amount, size, offset)
            query = self._get_query(template, seeds)
            queries.append(query)
        return queries

    def _fetch_seeds(self, session, table_name: str,
                     in_column: str) -> pd.DataFrame:
        Log.info(f"Fetching seeds from {table_name}.{in_column}")
        table = Table(table_name, MetaData(), autoload_with=session.bind)
        seeds = pd.read_sql(select(table.c[in_column]), session.bind)
        Log.info(f"Total seeds in {table_name}.{in_column}: {len(seeds)}")
        return seeds

    def _prepare_df(self, template: str, out_column: str,
                    batch_size: int) -> pd.DataFrame:
        data = [{'id': i + 1, out_column: template} for i in range(batch_size)]
        df = pd.DataFrame(data)
        return df

    @with_db_session
    def flow(self, df: pd.DataFrame, session=None, **kwargs) -> pd.DataFrame:
        Log.info("Starting QueryGenerationPipe")
        template_path = self.config["prompt"]["template"]
        seed_amount = self.config["seed_amount"]
        seed_length = self.config["seed_length"]
        seed_offset = self.config["seed_offset"]
        batch_size = self.config["batch_size"]
        if_exists = self.config["if_exists"]

        template = TemplateLoader.load(template_path)
        in_config = self.config["input"][0]
        out_config = self.config["output"][0]
        table_name = in_config["table"]
        in_column = in_config["columns"][0]
        out_table = out_config["table"]
        out_column = out_config["columns"][0]

        df = self._prepare_df(template, out_column, batch_size)
        seeds = self._fetch_seeds(session, table_name, in_column)
        queries = self._generate_queries(seeds, seed_amount, seed_length,
                                         seed_offset, template, batch_size)

        Log.info(f"Prepared DataFrame: {df.head()}")
        Log.info(f"Shape: {df.shape}")
        Log.info(f"Queries Generated: {len(queries)}")
        Log.info(f"ID Column Length: {len(df['id'])}")

        df = pd.DataFrame({"id": df['id'], out_column: queries})
        self._write_to_db(df, session, out_table, if_exists)

        Log.info("Finished QueryGenerationPipe")
        return df
