# @file thinking_dataset/pipeworks/pipes/export_tables_pipe.py
# @description Pipe for exporting tables.
# @version 1.2.31
# @license MIT

import pandas as pd
import sqlalchemy as sa
import thinking_dataset.config as config
from .pipe import Pipe
from ...io.files import Files
from thinking_dataset.utils.log import Log
from ...db.database import Database
from thinking_dataset.config.config_keys import ConfigKeys as Keys


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

    def _generate_output_path(self, table: str, template: str,
                              file_format: str, out_path: str) -> str:
        instance = config.initialize()
        name = instance.get_value(Keys.DATABASE_NAME)
        file = template.format(database_name=name,
                               table_name=table,
                               file_ext=f".{file_format}")
        return Files.get_file_path(out_path, file)

    def _export_data(self, df: pd.DataFrame, out_path: str, format: str):
        if format == "parquet":
            df.to_parquet(out_path, index=False)
        elif format == "csv":
            df.to_csv(out_path, index=False)
        else:
            raise ValueError(f"Unsupported file format: {format}")

    def _fetch_data_from_database(self, table: str,
                                  db: Database) -> pd.DataFrame:
        return db.fetch_data(table)

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        db = Database()
        instance = config.initialize()
        columns = self.config.get("columns", ["auto"])
        tables = self.config.get("tables", ["auto"])
        format = instance.get_value(Keys.DATASET_TYPE)
        out_path = instance.get_value(Keys.EXPORT_PATH)
        template = self.config.get("template")

        if not template:
            raise ValueError("File template is not set in the configuration.")

        if "auto" in tables:
            tables = self._fetch_all_tables(db)

        Log.info("Starting ExportTablesPipe")
        Log.info(f"Exporting columns: {columns}")
        Log.info(f"Output path: {out_path}")
        Log.info(f"File format: {format}")
        Log.info(f"Exporting tables: {tables}")

        Files.make_dir(path=out_path)

        for table in tables:
            df = self._fetch_data_from_database(table, db)
            if "auto" in columns:
                columns = self._fetch_table_columns(table, db)
            df = df[columns] if columns != ["auto"] else df
            out_path = self._generate_output_path(table, template, format,
                                                  out_path)
            self._export_data(df, out_path, format)
            Log.info(f"Exported table {table} to {out_path}")

        Log.info("Finished ExportTablesPipe")

        return df
