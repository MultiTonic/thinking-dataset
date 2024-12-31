"""
@file thinking_dataset/datasets/base_dataset.py
@description Provides common functionalities for dataset operations.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|GitHub Organization}
"""

import os
import sys
import pandas as pd
from thinking_dataset.db.database import Database
from ..utilities.log import Log


class BaseDataset:
    """
    A base class that provides common dataset operations and logging
    functionalities.
    """

    def __init__(self, data_tonic, config):
        """
        Constructs all the necessary attributes for the BaseDataset object.
        """
        self.log = Log.setup(self.__class__.__name__)
        self.data_tonic = data_tonic
        self.config = config

    def get_path(self, dataset_id=None):
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
            Log.error(self.log,
                      f"Error constructing dataset path: {e}",
                      exc_info=True)
            return None

    def list_files(self, data_dir):
        """
        List dataset files in the specified directory.
        """
        try:
            dataset_files = self.data_tonic.get_file_list.execute(
                data_dir)  # Use get_file_list operation
            Log.info(self.log,
                     f"Listed files in directory {data_dir}: {dataset_files}")
            return dataset_files
        except Exception as e:
            Log.error(self.log,
                      f"Error listing files in directory {data_dir}: {e}",
                      exc_info=True)
            return []

    def create(self, db_url, db_config):
        """
        Create a Database instance.
        """
        try:
            database = Database(url=db_url, config_path=db_config)
            Log.info(self.log, f"Created database instance with URL: {db_url}")
            return database
        except Exception as e:
            Log.error(self.log,
                      f"Error creating database instance: {e}",
                      exc_info=True)
            sys.exit(1)

    def load(self, database, data_dir):
        """
        Load dataset files into the database.
        """
        dataset_files = self.list_files(data_dir)
        parquet_files = [os.path.join(data_dir, f) for f in dataset_files]

        with database.get_session() as session:
            try:
                for file_path in parquet_files:
                    df = pd.read_parquet(file_path)
                    table_name = os.path.splitext(
                        os.path.basename(file_path))[0]
                    df.to_sql(table_name,
                              con=database.engine,
                              if_exists='append',
                              index=False)
                session.commit()
                self.log.info(
                    "Successfully loaded dataset files into the database.")
                return True
            except Exception as e:
                session.rollback()
                Log.error(self.log,
                          f"Error loading dataset files: {e}",
                          exc_info=True)
                return False

    def download(self, token, dataset_id):
        """
        Downloads the dataset from Hugging Face.
        """
        try:
            dataset_info = self.data_tonic.get_info.execute(dataset_id)
            if dataset_info:
                Log.info(self.log, f"Downloading dataset {dataset_id}...")

                download_urls = self.data_tonic.get_download_urls.execute(
                    dataset_id)
                for url in download_urls:
                    self.data_tonic.get_download_file.execute(
                        dataset_id, url, self.config['DATA_DIR'], token)

                Log.info(self.log,
                         f"Dataset {dataset_id} downloaded successfully.")
                return True
            else:
                Log.error(self.log,
                          f"Dataset {dataset_id} not found.",
                          exc_info=True)
                return False
        except Exception as e:
            Log.error(self.log,
                      f"Error downloading dataset {dataset_id}: {e}",
                      exc_info=True)
            return False
