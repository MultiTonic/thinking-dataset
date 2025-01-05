"""
@file thinking_dataset/datasets/base_dataset.py
@description A base class providing common dataset operations and logging.
@version 1.0.0
@license MIT
"""

import os
import pandas as pd
from dotenv import load_dotenv
from typing import List, Union, Optional
from ..db.database import Database
from ..utilities.log import Log


class BaseDataset:
    """
    A base class that provides common dataset operations and logging functions.
    """

    def __init__(self, data_tonic, config):
        self.log = Log.setup(self.__class__.__name__)
        self.data_tonic = data_tonic
        self.config = config

        load_dotenv()
        self.root_dir = os.path.abspath(
            self.config.get("paths", {}).get("root", "."))
        self.data_dir = os.path.join(
            self.root_dir,
            self.config.get("paths", {}).get("data", "data"))
        self.raw_dir = os.path.join(self.data_dir, "raw")
        self.processed_dir = os.path.join(self.data_dir, "processed")

    def get_path(self,
                 dataset_id: Optional[str] = None) -> Union[str, dict, None]:
        try:
            if dataset_id:
                dataset_info = self.data_tonic.get_info.execute(dataset_id)
                Log.info(self.log, f"Retrieved dataset info: {dataset_info}")
                return dataset_info
            path = f"{self.data_tonic.organization}/{self.data_tonic.dataset}"
            Log.info(self.log, f"Constructed dataset path: {path}")
            return path
        except Exception as e:
            Log.error(self.log, f"Error constructing dataset path: {e}")

    def list_files(self, dir_path: str) -> Optional[List[str]]:
        try:
            dataset_files = [
                f for f in os.listdir(dir_path)
                if os.path.isfile(os.path.join(dir_path, f))
            ]
            Log.info(self.log,
                     f"Listed files in directory {dir_path}: {dataset_files}")
            return dataset_files
        except Exception as e:
            Log.error(self.log,
                      f"Error listing files in directory {dir_path}: {e}")

    def create(self, db_url: str, config: str) -> Optional[Database]:
        try:
            database = Database(url=db_url, config_path=config)
            Log.info(self.log, f"Created database instance with URL: {db_url}")
            return database
        except Exception as e:
            Log.error(self.log, f"Error creating database instance: {e}")

    def load(self,
             database: Database,
             files_to_load: Optional[List[str]] = None) -> bool:
        if not files_to_load:
            Log.error(self.log, "No files to load provided.")
            return False

        parquet_files = [
            os.path.join(self.processed_dir, os.path.basename(f))
            for f in files_to_load
        ]
        Log.info(self.log, f"Parquet files to be loaded: {parquet_files}")

        try:
            files_in_directory = os.listdir(self.processed_dir)
            Log.info(
                self.log, "Files in directory "
                f"{self.processed_dir}: {files_in_directory}")
        except Exception as e:
            Log.error(self.log,
                      f"Error listing directory {self.processed_dir}: {e}")
            return False

        with database.get_session() as session:
            for file_path in parquet_files:
                try:
                    Log.info(self.log, f"Attempting to load file: {file_path}")
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"File not found: {file_path}")
                    df = pd.read_parquet(file_path)
                    Log.info(self.log, f"DataFrame columns: {df.columns}")
                    table_name = os.path.splitext(
                        os.path.basename(file_path))[0]
                    df.to_sql(table_name,
                              con=database.engine,
                              if_exists='append',
                              index=False)
                except FileNotFoundError as e:
                    Log.error(self.log, f"{e}")
                    session.rollback()
                    return False
                except Exception as e:
                    Log.error(self.log,
                              f"Error loading file {file_path}: {e}",
                              exc_info=True)
                    session.rollback()
                    return False
            try:
                session.commit()
                Log.info(
                    self.log,
                    "Successfully loaded dataset files into the database.")
                return True
            except Exception as e:
                session.rollback()
                Log.error(self.log, f"Error committing the session: {e}")
                return False

    def filter_files(self, all_files: List[str], include_files: List[str],
                     exclude_files: List[str]) -> List[str]:
        """
        Filter dataset files based on include and exclude lists.
        """
        Log.info(self.log, f"Initial files: {all_files}")
        Log.info(self.log, f"Include filter: {include_files}")
        Log.info(self.log, f"Exclude filter: {exclude_files}")
        if include_files:
            all_files = [file for file in all_files if file in include_files]
        if exclude_files:
            all_files = [
                file for file in all_files if file not in exclude_files
            ]
        Log.info(self.log, f"Filtered files: {all_files}")
        return all_files

    def download(self,
                 token: str,
                 dataset_id: str,
                 data_dir: str,
                 include_files: List[str] = [],
                 exclude_files: List[str] = []) -> bool:
        try:
            dataset_info = self.data_tonic.get_info.execute(dataset_id)
            if dataset_info:
                Log.info(self.log, f"Downloading dataset {dataset_id}...")

                download_urls = self.data_tonic.get_download_urls.execute(
                    dataset_id)
                filtered_urls = self.filter_files(download_urls, include_files,
                                                  exclude_files)

                for url in filtered_urls:
                    self.data_tonic.get_download_file.execute(
                        dataset_id, url, data_dir, token)

                Log.info(self.log,
                         f"Dataset {dataset_id} downloaded successfully.")
                return True
            else:
                Log.error(self.log, f"Dataset {dataset_id} not found.")
                return False
        except Exception as e:
            Log.error(self.log, f"Error downloading dataset {dataset_id}: {e}")
            return False
