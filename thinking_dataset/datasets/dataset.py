# @file thinking_dataset/datasets/dataset.py
# @description Implementation of the Dataset class.
# @version 1.0.7
# @license MIT

import os
import pandas as pd
from thinking_dataset.utils.log import Log
from ..db.database import Database
import thinking_dataset.config as config
from ..io.files import Files
from typing import List, Optional
from ..tonics.data_tonic import DataTonic


class Dataset:
    """
    A class for dataset operations.
    """

    def __init__(self, data_tonic: DataTonic):
        if not data_tonic:
            raise ValueError("Data tonic is required.")

        try:
            self.api = data_tonic
            self.database = Database()
            config_instance = config.initialize()
            self.org = config_instance.get_env_value(config.get_keys().HF_ORG)
            self.name = config_instance.get_value(
                config.get_keys().DATASET_NAME)
            self.type = config_instance.get_value(
                config.get_keys().DATASET_TYPE)
            self.include = config_instance.get_value(
                config.get_keys().INCLUDE_FILES)
            self.exclude = config_instance.get_value(
                config.get_keys().EXCLUDE_FILES)

            if not self.name:
                raise ValueError("Dataset name is not configured.")
            if not self.org:
                raise ValueError("Organization is not configured.")
            if not self.database:
                raise ValueError("Error creating database instance.")

            Log.info("Dataset initialized successfully!")
        except Exception as e:
            raise RuntimeError(f"Error initializing Dataset: {e}")

    def get_repo_id(self) -> str:
        try:
            path = f"{self.org}/{self.name}"
            return path
        except Exception as e:
            raise RuntimeError(f"Error constructing dataset path: {e}")

    def list_files(self, path: str) -> Optional[List[str]]:
        try:
            files = Files.list(path)
            Log.info(f"Listed files in directory {path}: {files}")
            return files
        except Exception as e:
            raise RuntimeError(f"Error listing files in directory {path}: {e}")

    def load(self,
             database: Database,
             files_to_load: Optional[List[str]] = None) -> bool:
        if not files_to_load:
            raise ValueError("No files to load provided.")

        Log.info(f"Parquet files to be loaded: {files_to_load}")

        try:
            path = Files.get_process_path()
            files = Files.list(path)
            Log.info(f"Files in directory {path}: {files}")
        except Exception as e:
            raise RuntimeError(f"Error listing directory {path}: {e}")

        with database.get_session() as session:
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
                              con=database.engine,
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

    def download(self) -> bool:
        try:
            config_instance = config.initialize()
            token = config_instance.get_env_value(
                config.get_keys().HF_READ_TOKEN)
            repo_id = self.get_repo_id()
            dataset_info = self.api.get_info.execute(repo_id)
            if dataset_info:
                Log.info(f"Downloading dataset {repo_id}...")

                download_urls = self.api.get_download_urls.execute(repo_id)
                filtered_urls = self.filter_files(download_urls, self.include,
                                                  self.exclude)

                path = Files.get_raw_path()
                for url in filtered_urls:
                    self.api.get_download_file.execute(repo_id, url, path,
                                                       token)

                Log.info(f"Dataset {repo_id} downloaded successfully.")
                return True
            else:
                raise ValueError(f"Dataset {repo_id} not found.")
        except Exception as e:
            raise RuntimeError(f"Error downloading dataset {repo_id}: {e}")
