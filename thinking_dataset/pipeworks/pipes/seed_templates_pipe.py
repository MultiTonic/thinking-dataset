# @file thinking_dataset/pipeworks/pipes/seed_templates_pipe.py
# @description Pipe for seeding templates with specific values using database.
# @version 1.6.1
# @license MIT

import json, random, re, pandas as pd  # noqa
from sqlalchemy import select, Table, MetaData, inspect
from typing import List, Dict
from tqdm import tqdm
from .pipe import Pipe
from thinking_dataset.utils.log import Log
from thinking_dataset.db.database import Database


class SeedTemplatesPipe(Pipe):

    def _fetch_random_seeds(self, column_data_df: pd.DataFrame,
                            seed_amount: int,
                            total_count: int) -> List[Dict[str, any]]:
        return [{
            'cable':
            column_data_df.iloc[random.randint(0, total_count - 1)]['cable']
        } for _ in range(seed_amount)]

    def _inject_seeds(self, template: str, seeds: List[Dict[str, any]]) -> str:
        return re.sub(r'\{\{\s*seeds\s*\}\}', json.dumps(seeds), template)

    def _get_next_table_name(self, session, base_name: str = "cable") -> str:
        Log.info("Fetching tables from the database")
        inspector = inspect(session.bind)
        tables = [
            table_name for table_name in inspector.get_table_names()
            if table_name.startswith(base_name)
            and re.match(r'.*-\d{5}$', table_name)
        ]
        Log.info(f"Found tables: {tables}")
        tables.sort()
        Log.info(f"Sorted tables: {tables}")
        if tables:
            last_table = tables[-1]
            Log.info(f"Last table in sequence: {last_table}")
            last_id = int(last_table.split('-')[-1])
            new_id = last_id + 1
            next_table_name = f"{base_name}-{new_id:05d}"
            Log.info(f"Next table name: {next_table_name}")
            return next_table_name
        next_table_name = f"{base_name}-00001"
        Log.info(f"Starting new table sequence: {next_table_name}")
        return next_table_name

    def _process(self, session, config: Dict[str, any],
                 results: pd.DataFrame) -> pd.DataFrame:
        table_name = config["input"][0]["table"]
        table = Table(table_name, MetaData(), autoload_with=session.bind)
        columns = config["input"][0]["columns"]
        column_data_df = pd.read_sql(select(table.c[columns[0]]), session.bind)
        row_count = len(column_data_df)
        Log.info(f"Total rows in the selected column: {row_count}")

        templates = []

        for _ in tqdm(range(config["batch_size"]),
                      desc="Generating Queries",
                      total=config["batch_size"],
                      unit="query"):
            seeds = self._fetch_random_seeds(column_data_df,
                                             config["seed_amount"], row_count)
            templates.append(
                self._inject_seeds(results["query"].iloc[0], seeds))

        results = pd.DataFrame({
            "id": range(1, config["batch_size"] + 1),
            config["output"][0]["columns"][0]: templates
        })

        next_table_name = self._get_next_table_name(session)
        results.to_sql(next_table_name,
                       session.bind,
                       if_exists='replace',
                       index=False)

        Log.info(
            f"Inserted {len(templates)} rows into '{next_table_name}' table")

        return results

    def flow(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        Log.info("Starting SeedTemplatesPipe")
        db, config = Database(), self.config
        with db.get_session() as session:
            df = self._process(session, config, df)
        Log.info(f"Total item count: {len(df)}")
        Log.info("Finished SeedTemplatesPipe")
        return df
