# @file thinking_dataset/pipeworks/pipes/export_tables_pipe.py
# @description Pipe for exporting tables.
# @version 1.1.0
# @license MIT

import pandas as pd
from .pipe import Pipe
from ...io.files import Files
from ...utilities.log import Log
from ...db.database import Database


class ExportTablesPipe(Pipe):
    """
    Pipe to export tables to the specified output directory.
    """

    def _log_start(self, df: pd.DataFrame):
        if "auto" in self.columns:
            self.columns = df.columns.tolist()

        Log.info(self.log, "Starting ExportTablesPipe")
        Log.info(self.log, f"Exporting columns: {self.columns}")
        Log.info(self.log, f"Output directory: {self.output_dir}")
        Log.info(self.log, f"File format: {self.file_format}")

    def _ensure_output_dir(self):
        self.files.make_dir(self.output_dir, self.log)

    def _select_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.columns]

    def _generate_output_path(self) -> str:
        file_name = f"{self.config['table_name']}_export.{self.file_format}"
        return self.files.get_path(self.output_dir, file_name)

    def _export_data(self, df: pd.DataFrame, output_path: str):
        if self.file_format == "parquet":
            df.to_parquet(output_path, index=False)
        elif self.file_format == "csv":
            df.to_csv(output_path, index=False)
        else:
            raise ValueError(f"Unsupported file format: {self.file_format}")

    def _log_finish(self, output_path: str):
        Log.info(self.log, f"Exported table to {output_path}")
        Log.info(self.log, "Finished ExportTablesPipe")

    def _fetch_data_from_database(self) -> pd.DataFrame:
        db_url = self.config.get('database_url')
        table_name = self.config.get('table_name')
        db = Database(url=db_url)
        return db.fetch_data(table_name)

    def flow(self, df: pd.DataFrame, log, **args) -> pd.DataFrame:
        self.files = Files(self.config)
        self.log = log
        self.output_dir = self.config.get("output_dir", "processed")
        self.columns = self.config.get("columns", ["auto"])
        self.file_format = self.config.get("file_format", "parquet")

        self._log_start(df)
        self._ensure_output_dir()

        df = self._fetch_data_from_database()
        df = self._select_columns(df)
        output_path = self._generate_output_path()

        self._export_data(df, output_path)
        self._log_finish(output_path)

        return df
