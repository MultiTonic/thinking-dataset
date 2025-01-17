# @file thinking_dataset/pipeworks/pipes/seed_templates_pipe.py
# @description Pipe for seeding templates with specific values.
# @version 1.0.94
# @license MIT

import json, re, pandas as pd  # noqa
from sqlalchemy import select, Table, MetaData, func
from typing import List, Dict, Any
from tqdm import tqdm
from .pipe import Pipe
from thinking_dataset.utils.log import Log
from thinking_dataset.db.database import Database


class SeedTemplatesPipe(Pipe):

    def _generate_query(self, table: Table, columns: List[str], limit: int,
                        offset: int) -> Any:
        return select(*[table.c[col] for col in columns]).order_by(
            func.random()).limit(limit).offset(offset)

    def _exec_query(self, session, query: Any,
                    columns: List[str]) -> List[Dict[str, Any]]:
        return [dict(zip(columns, row)) for row in session.execute(query)]

    def _fetch_seeds(self, session, table_name: str, columns: List[str],
                     limit: int, offset: int, seed_length: int,
                     seed_offset: int) -> pd.DataFrame:
        table = Table(table_name, MetaData(), autoload_with=session.bind)
        query = self._generate_query(table, columns, limit, offset)
        batch = self._exec_query(session, query, columns)
        seeds = []
        for seed in batch:
            for key in seed:
                seed[key] = seed[key][seed_offset:seed_offset + seed_length]
            seeds.append(seed)
        return pd.DataFrame(seeds, columns=columns)

    def _inject_seeds(self, template: str, seeds: List[Dict[str, Any]]) -> str:
        return re.sub(r'\{\{\s*seeds\s*\}\}', json.dumps(seeds), template)

    def _sample_seeds(self, seeds: pd.DataFrame,
                      seed_amount: int) -> List[Dict[str, Any]]:
        return seeds.sample(n=min(seed_amount, len(seeds))).to_dict(
            orient="records")

    def _process(self, session, config: Dict[str, Any],
                 df: pd.DataFrame) -> pd.DataFrame:
        seeds = self._fetch_seeds(session, config["input"][0]["table"],
                                  config["input"][0]["columns"],
                                  config["batch_size"], config["offset"],
                                  config["seed_length"], config["seed_offset"])
        queries = []

        for _ in tqdm(range(config["batch_size"]),
                      desc="Generating Queries",
                      total=config["batch_size"],
                      unit="query"):
            sampled_seeds = self._sample_seeds(seeds, config["seed_amount"])
            query = self._inject_seeds(df["query"].iloc[0], sampled_seeds)
            queries.append(query)

        return pd.DataFrame({
            "id": range(1, config["batch_size"] + 1),
            config["output"][0]["columns"][0]: queries
        })

    def _get_config(self) -> Dict[str, Any]:
        try:
            return {
                "input": self.config["input"],
                "output": self.config["output"],
                "batch_size": self.config.get("batch_size", 1000000),
                "offset": self.config.get("offset", 0),
                "seed_amount": self.config.get("seed_amount", 3),
                "seed_length": self.config.get("seed_length", 10000),
                "seed_offset": self.config.get("seed_offset", 0)
            }
        except KeyError as e:
            Log.error(f"Missing configuration key: {e}")
            raise

    def flow(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        Log.info("Starting SeedTemplatesPipe")
        db = Database()
        config = self._get_config()
        with db.get_session() as session:
            df = self._process(session, config, df)
        Log.info(f"Total item count: {len(df)}")

        Log.info("Finished SeedTemplatesPipe")
        return df
