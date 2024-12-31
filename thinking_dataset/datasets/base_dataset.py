"""
@file thinking_dataset/datasets/base_dataset.py
@description A base class providing common dataset operations and logging.
@version 1.0.0
@license MIT
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from typing import List, Union, Optional
from thinking_dataset.db.database import Database
from ..utilities.log import Log


class BaseDataset:
    """
    A base class that provides common dataset operations and logging functions.
    """

    def __init__(self, data_tonic, config):
        """
        Constructs all the necessary attributes for the BaseDataset object.
        """
        self.log = Log.setup(self.__class__.__name__)
        self.data_tonic = data_tonic
        self.config = config

        # Load environment variables
        load_dotenv()
        self.root_dir = os.path.abspath(
            self.config.get("paths", {}).get("root", "."))
        self.data_dir = os.path.join(
            self.root_dir,
            self.config.get("paths", {}).get("data", "data"))
        self.raw_dir = os.path.join(self.data_dir, "raw")

    def get_path(self,
                 dataset_id: Optional[str] = None) -> Union[str, dict, None]:
        """
        Constructs the path for the dataset within the organization.
        """
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

    def list_files(self) -> Optional[List[str]]:
        """
        List dataset files in the raw directory.
        """
        try:
            dataset_files = self.data_tonic.get_file_list.execute(self.raw_dir)
            Log.info(
                self.log,
                f"Listed files in directory {self.raw_dir}: {dataset_files}")
            return dataset_files
        except Exception as e:
            Log.error(self.log,
                      f"Error listing files in directory {self.raw_dir}: {e}")

    def create(self, db_url: str, db_config: str) -> Optional[Database]:
        """
        Create a Database instance.
        """
        try:
            database = Database(url=db_url, config_path=db_config)
            Log.info(self.log, f"Created database instance with URL: {db_url}")
            return database
        except Exception as e:
            Log.error(self.log, f"Error creating database instance: {e}")

    def load(self,
             database: Database,
             files_to_load: Optional[List[str]] = None) -> bool:
        """
        Load dataset files into the database.
        """
        if files_to_load is None:
            files_to_load = self.list_files()

        if not files_to_load:
            Log.error(self.log, "No files found in the data directory.")
            sys.exit(1)

        parquet_files = [os.path.join(self.raw_dir, f) for f in files_to_load]
        Log.info(self.log, f"Parquet files to be loaded: {parquet_files}")

        # Log the contents of the raw directory to verify if the files exist
        try:
            files_in_directory = os.listdir(self.raw_dir)
            Log.info(
                self.log,
                f"Files in directory {self.raw_dir}: {files_in_directory}")
        except Exception as e:
            Log.error(self.log, f"Error listing directory {self.raw_dir}: {e}")
            sys.exit(1)

        with database.get_session() as session:
            for file_path in parquet_files:
                try:
                    Log.info(self.log, f"Attempting to load file: {file_path}")
                    df = pd.read_parquet(file_path)
                    Log.info(self.log, f"DataFrame columns: {df.columns}")
                    table_name = os.path.splitext(
                        os.path.basename(file_path))[0]
                    df.to_sql(table_name,
                              con=database.engine,
                              if_exists='append',
                              index=False)
                except FileNotFoundError:
                    Log.error(self.log, f"File not found: {file_path}")
                    session.rollback()
                    sys.exit(1)
                except Exception as e:
                    Log.error(self.log,
                              f"Error loading file {file_path}: {e}",
                              exc_info=True)
                    session.rollback()
                    sys.exit(1)
            try:
                session.commit()
                Log.info(
                    self.log,
                    "Successfully loaded dataset files into the database.")
                return True
            except Exception as e:
                session.rollback()
                Log.error(self.log, f"Error committing the session: {e}")
                sys.exit(1)

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
        """
        Downloads the dataset from Hugging Face with filtering options.
        """
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
