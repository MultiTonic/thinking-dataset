# @file thinking_dataset/pipeworks/pipes/seed_templates_pipe.py
# @description Pipe for seeding templates with specific values using database.
# @version 1.3.0
# @license MIT

import json, re, pandas as pd  # noqa
from sqlalchemy import select, Table, MetaData, func
from typing import List, Dict
from tqdm import tqdm
from .pipe import Pipe
from thinking_dataset.utils.log import Log
from thinking_dataset.db.database import Database
from datetime import datetime
import random


class SeedTemplatesPipe(Pipe):

    def _fetch_single_random_seed(self, session, table_name: str,
                                  columns: List[str]) -> Dict[str, any]:
        table = Table(table_name, MetaData(), autoload_with=session.bind)
        total_count = session.execute(select(
            func.count()).select_from(table)).scalar()
        random_offset = random.randint(0, total_count - 1)
        query = select(*[table.c[col]
                         for col in columns]).offset(random_offset).limit(1)
        result = session.execute(query).first()
        return dict(zip(columns, result))

    def _inject_seeds(self, template: str, seeds: List[Dict[str, any]]) -> str:
        return re.sub(r'\{\{\s*seeds\s*\}\}', json.dumps(seeds), template)

    def _process(self, session, config: Dict[str, any],
                 df: pd.DataFrame) -> pd.DataFrame:
        table_name, columns = config["input"][0]["table"], config["input"][0][
            "columns"]
        timestamp = datetime.now()
        queries = []

        Log.info("Starting generation loop")
        for _ in tqdm(range(config["batch_size"]),
                      desc="Generating Queries",
                      total=config["batch_size"],
                      unit="query"):
            seeds = [
                self._fetch_single_random_seed(session, table_name, columns)
                for _ in range(config["seed_amount"])
            ]
            queries.append(self._inject_seeds(df["query"].iloc[0], seeds))

        Log.info("Inserting generated queries into the database")
        pd.DataFrame({
            "id": range(1, config["batch_size"] + 1),
            config["output"][0]["columns"][0]: queries
        }).to_sql(config["output"][0]["table"],
                  session.bind,
                  if_exists='replace',
                  index=False)

        return pd.DataFrame({
            "table_name": [config["output"][0]["table"]],
            "generation_timestamp": [timestamp.isoformat()],
            "pipeline_config_hash": [hash(str(config))],
            "template_used": [self.config.get("template")],
            "data_source": [table_name],
            "generation_count": [config["batch_size"]],
            "execution_duration":
            [(datetime.now() - timestamp).total_seconds()]
        })

    def flow(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        Log.info("Starting SeedTemplatesPipe")
        db, config = Database(), self.config
        with db.get_session() as session:
            df = self._process(session, config, df)
        Log.info(f"Total item count: {len(df)}")
        Log.info("Finished SeedTemplatesPipe")
        return df
