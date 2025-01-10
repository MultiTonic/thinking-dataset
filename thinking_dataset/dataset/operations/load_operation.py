# @file thinking_dataset/datasets/operations/load_operation.py
# @description Implementation of the LoadOperation class.
# @version 1.0.0
# @license MIT

import os
import pandas as pd
from thinking_dataset.utils.log import Log
from thinking_dataset.io.files import Files
from ...db.database import Database


class LoadOperation:
    """
    A class for handling dataset loading.
    """

    def __init__(self, database: Database):
        self.database = database

    def execute(self, files_to_load: list) -> bool:
        if not files_to_load:
            raise ValueError("No files to load provided.")

        Log.info(f"Parquet files to be loaded: {files_to_load}")

        try:
            path = Files.get_process_path()
            files = Files.list(path)
            Log.info(f"Files in directory {path}: {files}")
        except Exception as e:
            raise RuntimeError(f"Error listing directory {path}: {e}")

        with self.database.get_session() as session:
            for file_path in files_to_load:
                try:
                    Log.info(f"Attempting to load file: {file_path}")
                    if not Files.exists(file_path):
                        raise FileNotFoundError(f"File not found: {file_path}")
                    df = pd.read_parquet(file_path)
                    Log.info(f"DataFrame columns: {df.columns}")
                    table_name = os.path.splitext(
                        os.path.basename(file_path))[0]
                    df.to_sql(table_name,
                              con=self.database.engine,
                              if_exists='append',
                              index=False)
                except FileNotFoundError as e:
                    session.rollback()
                    raise FileNotFoundError(f"{e}")
                except Exception as e:
                    session.rollback()
                    raise RuntimeError(f"Error loading file {file_path}: {e}")
            try:
                session.commit()
                Log.info(
                    "Successfully loaded dataset files into the database.")
                return True
            except Exception as e:
                session.rollback()
                raise RuntimeError(f"Error committing the session: {e}")
