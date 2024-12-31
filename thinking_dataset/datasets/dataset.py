"""
@file thinking_dataset/datasets/dataset.py
@description Implementation of the Dataset class extending BaseDataset.
@version 1.0.0
@license MIT
"""

import os
import sys
from ..tonics.data_tonic import DataTonic
from ..datasets.base_dataset import BaseDataset
from ..config.dataset_config import DatasetConfig
from ..config.database_config import DatabaseConfig
from ..utilities.log import Log


class Dataset(BaseDataset):
    """
    A class for dataset operations extending the BaseDataset.
    """

    def __init__(self, data_tonic: DataTonic):
        """
        Constructs all the necessary attributes for the Dataset object.
        """
        self.log = Log.setup(self.__class__.__name__)
        try:
            self.data_tonic = data_tonic

            # Load and validate dataset configuration
            dataset_config_path = os.getenv('DATASET_CONFIG_PATH')
            dataset_config = DatasetConfig(dataset_config_path)
            dataset_config.validate()

            self.name = dataset_config.HF_DATASET
            self.id = None

            self.config = {
                'DATASET_TYPE': dataset_config.DATASET_TYPE,
                'DATABASE_URL':
                dataset_config.DATABASE_URL.format(name=self.name),
                'DATA_DIR': os.getenv('DATA_DIR', 'data'),
                'INCLUDE_FILES': dataset_config.INCLUDE_FILES,
                'EXCLUDE_FILES': dataset_config.EXCLUDE_FILES
            }

            # Log the contents of self.config for debugging
            Log.info(self.log, f"Dataset configuration: {self.config}")

            super().__init__(data_tonic, self.config)

            # Use DATABASE_URL from dataset config
            self.db_url = self.config['DATABASE_URL']

            # Load and validate database configuration
            database_config_path = os.getenv('DATABASE_CONFIG_PATH')
            db_config = DatabaseConfig(database_config_path)
            db_config.validate()

            # Log the contents of db_config for debugging
            Log.info(self.log, f"Database configuration: {db_config.__dict__}")

            self.database = self.create(self.db_url, database_config_path)
            Log.info(self.log, "Dataset initialized successfully.")
        except Exception as e:
            Log.error(self.log,
                      f"Error initializing Dataset: {e}",
                      exc_info=True)
            sys.exit(1)
