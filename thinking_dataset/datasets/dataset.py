# @file thinking_dataset/datasets/dataset.py
# @description Implementation of the Dataset class.
# @version 1.0.0
# @license MIT

import os
import sys
import pandas as pd
from ..utilities.log import Log
from ..db.database import Database
from ..config.config import Config
from typing import List, Union, Optional
from ..tonics.data_tonic import DataTonic


class Dataset:
    """
    A class for dataset operations.
    """

    def __init__(self, data_tonic: DataTonic):
        try:
            self.data_tonic = data_tonic
            self.config = Config.get()
            self.name = self.config.dataset_name
            self.id = None

            self.root_path = self.config.root_path
            self.data_path = self.config.data_path
            self.raw_dir = self.config.raw_path
            self.processed_dir = os.path.join(self.root_path,
                                              self.config.processed_path)

            self.database = Database(config=self.config)

            if not self.database:
                raise ValueError("Error creating database instance.")

            Log.info("Dataset initialized successfully!")
        except Exception as e:
            Log.error(f"Error initializing Dataset: {e}", exc_info=True)
            sys.exit(1)

    def get_path(self,
                 dataset_id: Optional[str] = None) -> Union[str, dict, None]:
        try:
            if dataset_id:
                dataset_info = self.data_tonic.get_info.execute(dataset_id)
                Log.info(f"Retrieved dataset info: {dataset_info}")
                return dataset_info
            path = f"{self.data_tonic.organization}/{self.data_tonic.dataset}"
            Log.info(f"Constructed dataset path: {path}")
            return path
        except Exception as e:
            Log.error(f"Error constructing dataset path: {e}")

    def list_files(self, dir_path: str) -> Optional[List[str]]:
        try:
            dataset_files = [
                f for f in os.listdir(dir_path)
                if os.path.isfile(os.path.join(dir_path, f))
            ]
            Log.info(f"Listed files in directory {dir_path}: {dataset_files}")
            return dataset_files
        except Exception as e:
            Log.error(f"Error listing files in directory {dir_path}: {e}")

    def load(self,
             database: Database,
             files_to_load: Optional[List[str]] = None) -> bool:
        if not files_to_load:
            Log.error("No files to load provided.")
            return False

        Log.info(f"Parquet files to be loaded: {files_to_load}")

        try:
            files_in_directory = os.listdir(self.processed_dir)
            Log.info("Files in directory "
                     f"{self.processed_dir}: {files_in_directory}")
        except Exception as e:
            Log.error(f"Error listing directory {self.processed_dir}: {e}")
            return False

        with database.get_session() as session:
            for file_path in files_to_load:
                try:
                    Log.info(f"Attempting to load file: {file_path}")
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"File not found: {file_path}")
                    df = pd.read_parquet(file_path)
                    Log.info(f"DataFrame columns: {df.columns}")
                    table_name = os.path.splitext(
                        os.path.basename(file_path))[0]
                    df.to_sql(table_name,
                              con=database.engine,
                              if_exists='append',
                              index=False)
                except FileNotFoundError as e:
                    Log.error(f"{e}")
                    session.rollback()
                    return False
                except Exception as e:
                    Log.error(f"Error loading file {file_path}: {e}",
                              exc_info=True)
                    session.rollback()
                    return False
            try:
                session.commit()
                Log.info(
                    "Successfully loaded dataset files into the database.")
                return True
            except Exception as e:
                session.rollback()
                Log.error(f"Error committing the session: {e}")
                return False

    def filter_files(self, all_files: List[str], include_files: List[str],
                     exclude_files: List[str]) -> List[str]:
        Log.info(f"Initial files: {all_files}")
        Log.info(f"Include filter: {include_files}")
        Log.info(f"Exclude filter: {exclude_files}")
        if include_files:
            all_files = [file for file in all_files if file in include_files]
        if exclude_files:
            all_files = [
                file for file in all_files if file not in exclude_files
            ]
        Log.info(f"Filtered files: {all_files}")
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
                Log.info(f"Downloading dataset {dataset_id}...")

                download_urls = self.data_tonic.get_download_urls.execute(
                    dataset_id)
                filtered_urls = self.filter_files(download_urls, include_files,
                                                  exclude_files)

                for url in filtered_urls:
                    self.data_tonic.get_download_file.execute(
                        dataset_id, url, data_dir, token)

                Log.info(f"Dataset {dataset_id} downloaded successfully.")
                return True
            else:
                Log.error(f"Dataset {dataset_id} not found.")
                return False
        except Exception as e:
            Log.error(f"Error downloading dataset {dataset_id}: {e}")
            return False
