# @file thinking_dataset/datasets/dataset.py
# @description Implementation of the Dataset class extending BaseDataset.
# @version 1.0.0
# @license MIT

import os
import sys
from ..tonics.data_tonic import DataTonic
from ..datasets.base_dataset import BaseDataset
from ..config.config import Config
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

            config_path = os.getenv('CONFIG_PATH')
            config = Config(config_path)
            config.validate()

            self.name = config.dataset_name
            self.id = None

            self.config = {
                'dataset_type': config.dataset_type,
                'database_url': config.database_url.format(name=self.name),
                'data_dir': os.getenv('data_dir', 'data'),
                'include_files': config.include_files,
                'exclude_files': config.exclude_files
            }

            Log.info(self.log, f"Dataset configuration: {self.config}")

            super().__init__(data_tonic, self.config)

            self.db_url = self.config['database_url']

            self.database = self.create(self.db_url, config_path)
            if not self.database:
                raise ValueError("Database instance creation failed.")

            Log.info(self.log, "Dataset initialized successfully.")
        except Exception as e:
            Log.error(self.log,
                      f"Error initializing Dataset: {e}",
                      exc_info=True)
            sys.exit(1)
