"""
@file project_root/thinking_dataset/config/dataset_config.py
@description Defines DatasetConfig class for storing dataset configuration.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from thinking_dataset.utilities.config_loader import ConfigLoader


class DatasetConfig:
    """
    Class for storing dataset configuration.
    """

    def __init__(self, config_path: str):
        loader = ConfigLoader(config_path)
        config = loader.get('dataset')
        self.HF_DATASET = config.get('HF_DATASET')
        self.DATASET_TYPE = config.get('DATASET_TYPE', 'parquet')
        self.DATABASE_URL = config.get('DATABASE_URL')

    def validate(self):
        """
        Validate the configuration settings.
        """
        if not self.HF_DATASET:
            raise ValueError("HF_DATASET must be set.")
        if not self.DATASET_TYPE:
            raise ValueError("DATASET_TYPE must be set.")
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set.")
