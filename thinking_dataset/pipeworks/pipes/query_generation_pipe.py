# @file thinking_dataset/pipeworks/pipes/query_generation_pipe.py
# @description Pipe for generating queries from templates and seeds.
# @version 1.1.1
# @license MIT

import json
import random
import re
import pandas as pd  # noqa
from tqdm import tqdm
from .pipe import Pipe
from typing import List, Dict
from thinking_dataset.utils.log import Log
from sqlalchemy import select, Table, MetaData
from thinking_dataset.db.database import Database
from tenacity import retry, stop_after_attempt, wait_fixed
from thinking_dataset.template.template_loader import TemplateLoader


class QueryGenerationPipe(Pipe):

    def __init__(self, config):
        super().__init__(config)
        self.template_column = "template"

    def _get_seeds(self, seeds: pd.DataFrame, amount: int, size: int,
                   offset: int) -> List[str]:
        seed_texts = []
        count = len(seeds)
        if count == 0:
            raise ValueError("No seeds available to generate.")
        for _ in range(amount):
            index = random.randint(0, count - 1)
            seed = seeds.iloc[index].values[0]
            seed_texts.append(seed[offset:offset + size])
        return seed_texts

    def _get_query(self, template: str, seeds: List[str]) -> str:
        value = ', '.join(json.dumps(seed) for seed in seeds)
        return re.sub(r'"{{\s*seeds\s*}}"', value, template)

    def _validate(self, df: pd.DataFrame, column: str):
        if column not in df.columns or df[column].iloc[0] is None:
            raise ValueError(f"DataFrame '{column}' column is invalid")

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2), reraise=True)
    def _write_to_db(self, df: pd.DataFrame, session, out_table: str,
                     if_exists: str):
        df.to_sql(out_table, session.bind, if_exists=if_exists, index=False)
        Log.info(f"Inserted {len(df)} rows into '{out_table}' table")

    def _generate_queries(self, df: pd.DataFrame, seeds: pd.DataFrame,
                          amount: int, size: int, offset: int,
                          batch_size: int) -> List[str]:
        self._validate(df, self.template_column)
        queries = [
            self._get_query(df[self.template_column].iloc[0],
                            self._get_seeds(seeds, amount, size, offset))
            for _ in tqdm(range(batch_size),
                          desc="Generating Queries",
                          total=batch_size,
                          unit="q")
        ]
        return queries

    def _fetch_seeds(self, session, table_name: str,
                     in_column: str) -> pd.DataFrame:
        table = Table(table_name, MetaData(), autoload_with=session.bind)
        seeds = pd.read_sql(select(table.c[in_column]), session.bind)
        Log.info(f"Total seeds in {table_name}.{in_column}: {len(seeds)}")
        return seeds

    def _prepare_dataframe(self, df: pd.DataFrame, template: str,
                           flush_df: bool) -> pd.DataFrame:
        if flush_df:
            df = self.flush(df, self.template_column)
        df[self.template_column] = [template] * len(df)
        df['id'] = df.get('id', range(1, len(df) + 1))
        return df

    def _load_template(self, template_path: str, schema_path: str) -> str:
        if template_path is None or schema_path is None:
            raise ValueError(
                "Template or schema path is not set in the configuration")
        Log.info(f"Template path: {template_path}")
        Log.info(f"Schema path: {schema_path}")
        return TemplateLoader(template_path, schema_path).load()

    def _process(self, session, config: Dict[str, any],
                 df: pd.DataFrame) -> pd.DataFrame:
        in_config = config["input"][0]
        out_config = config["output"][0]
        table_name = in_config["table"]
        in_column = in_config["columns"][0]
        out_table = out_config["table"]
        out_column = out_config["columns"][0]
        template_path = config["prompt"]["template"]
        schema_path = config["prompt"]["schema"]
        flush_df = config["flush"]

        template = self._load_template(template_path, schema_path)

        df = self._prepare_dataframe(df, template, flush_df)
        seeds = self._fetch_seeds(session, table_name, in_column)
        queries = self._generate_queries(df, seeds, config["seed_amount"],
                                         config["seed_length"],
                                         config["seed_offset"],
                                         config["batch_size"])
        df = pd.DataFrame({"id": df['id'], out_column: queries})
        self._write_to_db(df, session, out_table, config["if_exists"])
        return df

    def flow(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        Log.info("Starting QueryGenerationPipe")
        with Database().get_session() as session:
            df = self._process(session, self.config, df)
        Log.info("Finished QueryGenerationPipe")
        return df
