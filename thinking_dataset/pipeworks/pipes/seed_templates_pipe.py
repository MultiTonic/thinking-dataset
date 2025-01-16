# @file thinking_dataset/pipeworks/pipes/seed_templates_pipe.py
# @description Pipe for seeding templates with specific values.
# @version 1.0.72
# @license MIT

import os, json, re, pandas as pd  # noqa
from sqlalchemy import select, Table, MetaData, func
from typing import List, Dict, Any
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from .pipe import Pipe
from thinking_dataset.config.config_keys import ConfigKeys as CK
from thinking_dataset.utils.log import Log
from thinking_dataset.db.database import Database
from thinking_dataset.io.files import Files


class SeedTemplatesPipe(Pipe):

    def _generate_query(self, table: Table, columns: List[str],
                        batch_size: int, offset: int) -> Any:
        return select(*[table.c[col] for col in columns]).order_by(
            func.random()).limit(batch_size).offset(offset)

    def _exec_query(self, session, query: Any,
                    columns: List[str]) -> List[Dict[str, Any]]:
        return [dict(zip(columns, row)) for row in session.execute(query)]

    def _fetch_seeds(self, session, table_name: str, columns: List[str],
                     batch_size: int, offset: int, seed_length: int,
                     seed_offset: int) -> pd.DataFrame:
        table = Table(table_name, MetaData(), autoload_with=session.bind)
        seeds = []
        while True:
            batch = self._exec_query(
                session,
                self._generate_query(table, columns, batch_size, offset),
                columns)
            if not batch:
                break
            for seed in batch:
                for key in seed:
                    seed[key] = seed[key][seed_offset:seed_offset +
                                          seed_length]
            seeds.extend(batch)
            offset += batch_size
        return pd.DataFrame(seeds, columns=columns)

    def _total_rows(self, session, table_name: str) -> int:
        table = Table(table_name, MetaData(), autoload_with=session.bind)
        return session.execute(select(
            func.count()).select_from(table)).scalar()

    def _inject_seeds(self, template: str, seeds: List[Dict[str, Any]]) -> str:
        return re.sub(r'\{\{\s*inject_seeds\s*\}\}', json.dumps(seeds),
                      template)

    def _save_to_parquet(self, df: pd.DataFrame, path: str):
        Files.make_dir(os.path.dirname(path))
        if Files.exists(path):
            existing_df = pd.read_parquet(path)
            df = pd.concat([existing_df, df], ignore_index=True)
        df.to_parquet(path, index=False)

    def _process_shard(self, shard_queries: List[str],
                       sampled_seeds: List[Dict[str, Any]], save_path: str,
                       save_file_template: str, batch_num: int,
                       total_batches: int, shard_idx: int):
        shard_df = pd.DataFrame({
            "id":
            range(shard_idx + 1, shard_idx + len(shard_queries) + 1),
            "query":
            [self._inject_seeds(q, sampled_seeds) for q in shard_queries]
        })
        file_path = Files.get_file_path(
            save_path,
            save_file_template.format(
                batch_info=f"{batch_num + 1:05d}-of-{total_batches:05d}"))
        self._save_to_parquet(shard_df, file_path)

    def _clear_db_session_cache(self, session):
        session.close_all()

    def _get_config(self) -> Dict[str, Any]:
        return {
            "tables":
            self.config["tables"],
            "batch_size":
            self.config.get("batch_size", 1000000),
            "shard_size":
            self.config.get("shard_size", 4096),
            "offset":
            self.config.get("offset", 0),
            "limit":
            self.config.get("limit", 3),
            "seed_length":
            self.config.get("seed_length", 10000),
            "seed_offset":
            self.config.get("seed_offset", 0),
            "save":
            self.config.get("save", False),
            "save_path":
            Files.get_path(CK.GENERATE_PATH),
            "save_file_template":
            self.config.get("save_file",
                            "seed-templates-pipe-{batch_info}.parquet"),
            "max_workers":
            self.config.get("max_workers", 4)
        }

    def _fetch_batch_data(self, session, config: Dict[str, Any],
                          offset: int) -> pd.DataFrame:
        return self._fetch_seeds(session, config["tables"][0]["table"],
                                 config["tables"][0]["columns"],
                                 config["batch_size"], offset,
                                 config["seed_length"], config["seed_offset"])

    def _sample_seeds(self, seeds: pd.DataFrame,
                      config: Dict[str, Any]) -> List[Dict[str, Any]]:
        return seeds.sample(n=min(config["limit"], 1000000)).to_dict(
            orient="records")

    def _process_shards(self, queries: List[str],
                        sampled_seeds: List[Dict[str, Any]],
                        config: Dict[str, Any], batch_num: int):
        with tqdm(total=config["batch_size"],
                  desc="Generating Shard Queries") as pbar:
            with ThreadPoolExecutor(
                    max_workers=config["max_workers"]) as executor:
                futures = {
                    executor.submit(self._process_shard, queries[i:i + config["shard_size"]], sampled_seeds, config["save_path"], config["save_file_template"], batch_num, config["total_batches"], i): # noqa
                    i
                    for i in range(0, config["batch_size"],
                                   config["shard_size"])
                }
                for _ in as_completed(futures):
                    pbar.update(config["shard_size"])

    def _process_batch(self, session, batch_num: int, config: Dict[str, Any],
                       df: pd.DataFrame):
        offset = config["offset"] + batch_num * config["batch_size"]
        seeds = self._fetch_batch_data(session, config, offset)
        sampled_seeds = self._sample_seeds(seeds, config)
        queries = [df["query"].iloc[0]] * config["batch_size"]
        self._process_shards(queries, sampled_seeds, config, batch_num)

    def flow(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        Log.info("Starting SeedTemplatesPipe")
        db = Database()
        config = self._get_config()
        with db.get_session() as session:
            config["total_batches"] = -(
                -self._total_rows(session, config["tables"][0]["table"]) //
                config["batch_size"])

            for batch_num in range(config["total_batches"]):
                self._process_batch(session, batch_num, config, df)

        Log.info("Finished SeedTemplatesPipe")
        return df
