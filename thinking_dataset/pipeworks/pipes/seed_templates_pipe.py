# @file thinking_dataset/pipeworks/pipes/seed_templates_pipe.py
# @description Pipe for seeding templates with specific values.
# @version 1.0.58
# @license MIT

import pandas as pd, json, re  # noqa
from sqlalchemy import select, Table, MetaData, func
from typing import List, Dict, Any, Tuple
from tqdm import tqdm
from .pipe import Pipe
from thinking_dataset.utils.log import Log
from thinking_dataset.db.database import Database


class SeedTemplatesPipe(Pipe):

    def generate_query(self, table_name: str, columns: List[str],
                       batch_size: int, offset: int) -> Any:
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=Database().engine)
        return select(*[table.c[col] for col in columns]).order_by(
            func.random()).limit(batch_size).offset(offset)

    def exec_query(self, db: Database, query: Any,
                   columns: List[str]) -> List[Dict[str, Any]]:
        with db.engine.connect() as connection:
            result = connection.execute(query)
            batch = [dict(zip(columns, row)) for row in result]
        return batch

    def scalar_result(self, db: Database, query: Any) -> int:
        with db.engine.connect() as connection:
            result = connection.execute(query)
            return result.scalar()

    def _fetch_seeds_batch(self, db: Database, table_name: str,
                           columns: List[str], batch_size: int,
                           offset: int) -> List[Dict[str, Any]]:
        query = self.generate_query(table_name, columns, batch_size, offset)
        Log.info(f"Executing query: {query} with offset: {offset}")
        return self.exec_query(db, query, columns)

    def _fetch_seeds_batches(self, db: Database, table_name: str,
                             columns: List[str], batch_size: int,
                             offset: int) -> List[Dict[str, Any]]:
        seeds = []
        while True:
            batch = self._fetch_seeds_batch(db, table_name, columns,
                                            batch_size, offset)
            if not batch:
                break
            seeds.extend(batch)
            offset += batch_size
        return seeds

    def _fetch_seeds(self, db: Database, table_name: str, columns: List[str],
                     batch_size: int, offset: int, seed_length: int,
                     seed_offset: int) -> pd.DataFrame:
        Log.info(f"Fetching seeds from '{table_name}' with columns: {columns} "
                 f"in batches of {batch_size} starting from offset {offset}")

        seeds = self._fetch_seeds_batches(db, table_name, columns, batch_size,
                                          offset)

        def truncate_seed(seed):
            return seed[seed_offset:seed_offset + seed_length]

        for seed in seeds:
            for key in seed:
                seed[key] = truncate_seed(seed[key])

        Log.info(f"Fetched {len(seeds)} seed values")
        return pd.DataFrame(seeds, columns=columns)

    def _total_rows(self, db: Database, table_name: str) -> int:
        query = select(func.count()).select_from(
            Table(table_name, MetaData(), autoload_with=db.engine))
        total = self.scalar_result(db, query)
        Log.info(f"Total rows in {table_name}: {total}")
        return total

    def _join_df(self, dfs: List[pd.DataFrame]) -> pd.DataFrame:
        return pd.concat(dfs, ignore_index=True)

    def _sample(self, df: pd.DataFrame, limit: int) -> List[Dict[str, Any]]:
        limit = min(limit, 1000000)
        return df.sample(n=limit).to_dict(orient="records")

    def _inject(self, template: str, seeds: List[Dict[str, Any]]) -> str:
        formatted_seeds = json.dumps(seeds)
        pattern = re.compile(r'\{\{\s*inject_seeds\s*\}\}')
        return pattern.sub(formatted_seeds, template)

    def _config_table(self, table_config: Dict[str,
                                               Any]) -> Tuple[str, List[str]]:
        table_name = table_config["table"]
        columns = table_config.get("columns", ["content"])
        return table_name, columns

    def _table_seeds(self, db: Database, table_name: str, columns: List[str],
                     batch_size: int, offset: int, seed_length: int,
                     seed_offset: int) -> pd.DataFrame:
        total_rows = self._total_rows(db, table_name)
        effective_offset = offset % total_rows
        return self._fetch_seeds(db, table_name, columns, batch_size,
                                 effective_offset, seed_length, seed_offset)

    def _get_seeds(self, db: Database, tables_config: List[Dict[str, Any]],
                   batch_size: int, offset: int, seed_length: int,
                   seed_offset: int) -> pd.DataFrame:
        seed_dfs = [
            self._table_seeds(db, *self._config_table(config), batch_size,
                              offset, seed_length, seed_offset)
            for config in tables_config
        ]
        return self._join_df(seed_dfs)

    def _apply_template(self, template: str,
                        sampled_seeds: List[Dict[str, Any]]) -> str:
        return self._inject(template, sampled_seeds)

    def flow(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        Log.info("Starting SeedTemplatesPipe")

        db = Database()
        tables_config = self.config.get("tables")
        batch_size = self.config.get("batch_size", 1000000)
        offset = self.config.get("offset", 0)
        limit = self.config.get("limit", 3)
        seed_length = self.config.get("seed_length", 1000)
        seed_offset = self.config.get("seed_offset", 0)

        seeds = self._get_seeds(db, tables_config, batch_size, offset,
                                seed_length, seed_offset)
        sampled_seeds = self._sample(seeds, limit)

        queries = [df["query"].iloc[0]] * batch_size

        updated_queries = []
        for query in tqdm(queries, desc="Generating Queries"):
            if self.abort_flag.is_set():
                break
            updated_queries.append(self._apply_template(query, sampled_seeds))

        df = pd.DataFrame({
            "id": range(1, batch_size + 1),
            "query": updated_queries
        })

        Log.info("Finished SeedTemplatesPipe")
        return df
