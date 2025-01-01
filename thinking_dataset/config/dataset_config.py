"""
@file project_root/thinking_dataset/config/dataset_config.py
@description Defines DatasetConfig class for storing dataset configuration.
@version 1.0.0
@license MIT
"""

from ..utilities.config_loader import ConfigLoader


class DatasetConfig:
    """
    Class for storing dataset configuration.
    """

    def __init__(self, config_path: str):
        loader = ConfigLoader(config_path)
        config = loader.get('dataset')
        self.HF_DATASET = config.get('hfapi', {}).get('name')
        self.DATASET_TYPE = config.get('hfapi', {}).get('type', 'parquet')
        self.DATABASE_URL = config.get('database', {}).get('url')
        self.ROOT_DIR = config.get('paths', {}).get('root', '.')
        self.DATA_DIR = config.get('paths', {}).get('data', 'data')
        self.RAW_DIR = config.get('paths', {}).get('raw', 'raw')
        self.PROCESSED_DIR = config.get('paths',
                                        {}).get('processed', 'processed')
        self.DB_DIR = config.get('paths', {}).get('database', 'db')
        self.INCLUDE_FILES = config.get('files', {}).get('include', [])
        self.EXCLUDE_FILES = config.get('files', {}).get('exclude', [])
        self.PIPELINES = config.get('pipelines', [])

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
        if not self.PIPELINES:
            raise ValueError("PIPELINES must be set.")
