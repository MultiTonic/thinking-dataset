# @file thinking_dataset/pipeworks/pipes/export_tables_pipe.py
# @description Pipe for exporting tables with consistent shapes.
# @version 1.2.39
# @license MIT

import pandas as pd
import sqlalchemy as sa
import thinking_dataset.config as conf
import thinking_dataset.config.config_keys as Keys
from .pipe import Pipe
from ...io.files import Files
from thinking_dataset.utils.log import Log
from ...db.database import Database

CK = Keys.ConfigKeys


class ExportTablesPipe(Pipe):
    """
    Pipe to export tables to the specified output directory.
    """

    def _fetch_all_tables(self, db: Database) -> list:
        inspector = sa.inspect(db.engine)
        return inspector.get_table_names()

    def _fetch_table_columns(self, table: str, db: Database) -> list:
        inspector = sa.inspect(db.engine)
        return [column['name'] for column in inspector.get_columns(table)]

    def _generate_out_path(self,
                           pattern: str,
                           file_type: str,
                           out_path: str,
                           shard_num=None,
                           total_shards=None) -> str:
        instance = conf.initialize()
        dataset_name = instance.get_value(CK.DATASET_NAME)
        split_name = 'train'
        split_info = f"{shard_num:05d}-of-{total_shards:05d}" \
            if shard_num is not None else ""
        file = pattern.format(dataset_name=dataset_name,
                              split_name=split_name,
                              split_info=split_info,
                              file_type=file_type)
        return Files.get_file_path(out_path, file)

    def _export_data(self, df: pd.DataFrame, out_path: str, file_type: str):
        if file_type == "parquet":
            df.to_parquet(out_path, index=False)
        elif file_type == "csv":
            df.to_csv(out_path, index=False)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _fetch_data_from_database(self, table: str,
                                  db: Database) -> pd.DataFrame:
        return db.fetch_data(table)

    def _remap_columns(self, df: pd.DataFrame, schema: list,
                       drop_columns: bool) -> pd.DataFrame:
        if drop_columns:
            if len(df.columns) > len(schema):
                df = df.iloc[:, :len(schema)]
            df.columns = schema
        else:
            for i, col in enumerate(schema):
                if i < len(df.columns):
                    df.rename(columns={df.columns[i]: col}, inplace=True)
        return df

    def _align_columns(self, df: pd.DataFrame, schema: list,
                       fill_value) -> pd.DataFrame:
        missing_cols = set(schema) - set(df.columns)
        for col in missing_cols:
            df[col] = fill_value
        return df[schema]

    def _merge_dataframes(self, dfs: list, schema: list, drop_columns: bool,
                          fill_value) -> pd.DataFrame:
        conformed_dfs = [
            self._remap_columns(df, schema, drop_columns) for df in dfs
        ]
        if not drop_columns:
            conformed_dfs = [
                self._align_columns(df, schema, fill_value)
                for df in conformed_dfs
            ]
        merged_df = pd.concat(conformed_dfs, ignore_index=True)
        return merged_df

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        db = Database()
        instance = conf.initialize()
        columns = self.config.get("columns", ["auto"])
        tables = self.config.get("tables", ["all"])
        file_type = instance.get_value(CK.DATASET_TYPE)
        out_path = self.config.get("path")
        shard_size = self.config.get("shard_size")
        pattern = self.config.get("pattern")
        expected_schema = self.config.get("schema")
        drop_columns = self.config.get("drop_columns", True)
        fill_value = self.config.get("fill_value", None)

        if not pattern:
            raise ValueError("File pattern is not set in the configuration.")
        if not expected_schema:
            raise ValueError("Schema is not set in the configuration.")

        if "all" in tables:
            tables = self._fetch_all_tables(db)

        Log.info("Starting ExportTablesPipe")
        Log.info(f"Exporting columns: {columns}")
        Log.info(f"Output path: {out_path}")
        Log.info(f"File type: {file_type}")
        Log.info(f"Exporting tables: {tables}")
        Log.info(f"Shard size: {shard_size}")
        Log.info(f"Drop columns: {drop_columns}")
        Log.info(f"Fill value: {fill_value}")

        Files.make_dir(path=out_path)

        dfs = []
        for table in tables:
            df = self._fetch_data_from_database(table, db)
            if "auto" in columns:
                columns = self._fetch_table_columns(table, db)
            df = df[columns] if columns != ["auto"] else df
            dfs.append(df)

        combined_df = self._merge_dataframes(dfs, expected_schema,
                                             drop_columns, fill_value)

        total_shards = (len(combined_df) + shard_size - 1) // shard_size
        for shard_num in range(total_shards):
            shard_df = combined_df[shard_num * shard_size:(shard_num + 1) *
                                   shard_size]
            output_path = self._generate_out_path(pattern, file_type, out_path,
                                                  shard_num, total_shards)
            self._export_data(shard_df, output_path, file_type)
            Log.info(f"Exported shard {shard_num + 1} to {output_path}")

        Log.info("Finished ExportTablesPipe")

        return combined_df
