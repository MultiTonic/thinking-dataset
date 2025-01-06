# @file project_root/thinking_dataset/pipeworks/pipes/export_tables_pipe.py
# @description Pipe for exporting tables.
# @version 1.2.13
# @license MIT

import pandas as pd
import sqlalchemy as sa
from .pipe import Pipe
from ...io.files import Files
from ...utilities.log import Log
from ...db.database import Database
from ...config.config import Config


class ExportTablesPipe(Pipe):
    """
    Pipe to export tables to the specified output directory.
    """

    def _log_start(self):
        if "auto" in self.columns:
            Log.info("Auto-setting columns from the database tables.")
        if "auto" in self.tables:
            Log.info("Auto-setting table names from the database.")

        Log.info("Starting ExportTablesPipe")
        Log.info(f"Exporting columns: {self.columns}")
        Log.info(f"Output directory: {self.output_dir}")
        Log.info(f"File format: {self.file_format}")
        Log.info(f"Exporting tables: {self.tables}")

    def _ensure_output_dir(self):
        self.files.make_dir(self.output_dir)

    def _select_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        if "auto" in self.columns:
            return df
        missing_columns = [
            col for col in self.columns if col not in df.columns
        ]
        if missing_columns:
            raise KeyError(
                f"None of {missing_columns} are in the DataFrame columns")
        return df[self.columns]

    def _generate_output_path(self, table: str) -> str:
        database_name = self.config.database_name
        export_file_template = Config.get_value(
            self.config.pipelines[1]['pipeline']['config'], 'export_file')
        file_name = export_file_template.format(
            database_name=database_name,
            table_name=table,
            file_ext=f".{self.file_format}")
        return self.files.get_path(self.output_dir, file_name)

    def _export_data(self, df: pd.DataFrame, output_path: str):
        if self.file_format == "parquet":
            df.to_parquet(output_path, index=False)
        elif self.file_format == "csv":
            df.to_csv(output_path, index=False)
        else:
            raise ValueError(f"Unsupported file format: {self.file_format}")

    def _fetch_data_from_database(self, table: str) -> pd.DataFrame:
        db = Database(config=self.config)
        return db.fetch_data(table)

    def _fetch_all_tables(self) -> list:
        db = Database(config=self.config)
        inspector = sa.inspect(db.engine)
        return inspector.get_table_names()

    def _fetch_table_columns(self, table: str) -> list:
        db = Database(config=self.config)
        inspector = sa.inspect(db.engine)
        return [column['name'] for column in inspector.get_columns(table)]

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        self.config = Config.get()
        self.files = Files(self.config)
        self.output_dir = Config.get_value(
            self.config, 'output_dir') or self.files.get_processed_path()
        self.columns = Config.get_value(self.config, 'columns') or ["auto"]
        self.tables = Config.get_value(self.config, 'tables') or ["auto"]
        self.file_format = Config.get_value(self.config,
                                            'file_format') or "parquet"

        if "auto" in self.tables:
            self.tables = self._fetch_all_tables()

        self._log_start()
        self._ensure_output_dir()

        for table in self.tables:
            df = self._fetch_data_from_database(table)
            if "auto" in self.columns:
                self.columns = self._fetch_table_columns(table)
            df = self._select_columns(df)
            output_path = self._generate_output_path(table)
            self._export_data(df, output_path)
            Log.info(f"Exported table {table} to {output_path}")

        Log.info("Finished ExportTablesPipe")

        return df
