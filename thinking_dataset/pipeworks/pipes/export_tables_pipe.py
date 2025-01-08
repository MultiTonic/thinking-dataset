# @file thinking_dataset/pipeworks/pipes/export_tables_pipe.py
# @description Pipe for exporting tables.
# @version 1.2.29
# @license MIT

import pandas as pd
import sqlalchemy as sa
from .pipe import Pipe
from ...io.files import Files
from ...utilities.log import Log
from ...db.database import Database
from ...config.config import Config
from ...config.config_keys import ConfigKeys as Keys


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

    def _generate_output_path(self, table: str, file_template: str,
                              file_format: str, output_dir: str) -> str:
        database_name = Config.get_value(Keys.DATABASE_NAME)
        file_name = file_template.format(database_name=database_name,
                                         table_name=table,
                                         file_ext=f".{file_format}")
        return Files.get_file_path(output_dir, file_name)

    def _export_data(self, df: pd.DataFrame, output_path: str,
                     file_format: str):
        if file_format == "parquet":
            df.to_parquet(output_path, index=False)
        elif file_format == "csv":
            df.to_csv(output_path, index=False)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def _fetch_data_from_database(self, table: str,
                                  db: Database) -> pd.DataFrame:
        return db.fetch_data(table)

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        db = Database()
        columns = self.config.get("columns", ["auto"])
        tables = self.config.get("tables", ["auto"])
        file_format = self.config.get("format", "parquet")
        output_dir = Config.get_value(Keys.EXPORT_PATH)
        file_template = self.config.get("template")

        if not file_template:
            raise ValueError("File template is not set in the configuration.")

        if "auto" in tables:
            tables = self._fetch_all_tables(db)

        Log.info("Starting ExportTablesPipe")
        Log.info(f"Exporting columns: {columns}")
        Log.info(f"Output directory: {output_dir}")
        Log.info(f"File format: {file_format}")
        Log.info(f"Exporting tables: {tables}")

        Files.make_dir(path=output_dir)

        for table in tables:
            df = self._fetch_data_from_database(table, db)
            if "auto" in columns:
                columns = self._fetch_table_columns(table, db)
            df = df[columns] if columns != ["auto"] else df
            output_path = self._generate_output_path(table, file_template,
                                                     file_format, output_dir)
            self._export_data(df, output_path, file_format)
            Log.info(f"Exported table {table} to {output_path}")

        Log.info("Finished ExportTablesPipe")

        return df
