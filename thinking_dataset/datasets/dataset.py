"""
@file thinking_dataset/datasets/dataset.py
@description Implementation of the Dataset class extending BaseDataset.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import sys
from thinking_dataset.tonics.data_tonic import DataTonic
from .base_dataset import BaseDataset
from ..utilities.log import Log


class Dataset(BaseDataset):
    """
    A class for dataset operations extending the BaseDataset.
    """

    def __init__(self, data_tonic: DataTonic, config: dict):
        """
        Constructs all the necessary attributes for the Dataset object.

        Parameters
        ----------
        data_tonic : DataTonic
            An instance of the DataTonic class containing config and token.
        config : dict
            Configuration for the dataset.
        """
        self.logger = Log.setup(__name__)  # Initialize logger first
        try:
            self.data_tonic = data_tonic
            self.config = config.get('dataset')
            if self.config is None:
                raise ValueError("Dataset configuration is missing.")

            super().__init__(data_tonic, self.config)

            # Format the database URL using the dataset name from env variables
            self.db_url = self.config['DATABASE_URL'].format(
                HF_DATASET=os.getenv("HF_DATASET"))

            # Initialize the db with the specific database URL or config path.
            db_config = config.get('database')
            self.database = self.create(self.db_url, db_config)
            Log.info(self.logger, "Dataset initialized successfully.")
        except Exception as e:
            Log.error(self.logger,
                      f"Error initializing Dataset: {e}",
                      exc_info=True)
            sys.exit(1)
