"""
@file project_root/thinking_dataset/config/dataset_config.py
@description Defines DatasetConfig class for storing dataset configuration.
@version 1.0.0
@license MIT
"""

from ..utilities.command_utils import CommandUtils
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
        self.LOAD_PATTERNS = config.get('files', {}).get(
            'load', ['{file_root}_prepare{file_ext}'])
        self.PIPELINES = config.get('pipelines', [])

    def validate(self):
        """
        Validate the configuration settings.
        """
        missing = []
        if not self.HF_DATASET:
            missing.append("HF_DATASET")
        if not self.DATASET_TYPE:
            missing.append("DATASET_TYPE")
        if not self.DATABASE_URL:
            missing.append("DATABASE_URL")
        if not self.ROOT_DIR:
            missing.append("ROOT_DIR")
        if not self.DATA_DIR:
            missing.append("DATA_DIR")
        if not self.RAW_DIR:
            missing.append("RAW_DIR")
        if not self.PROCESSED_DIR:
            missing.append("PROCESSED_DIR")
        if not self.DB_DIR:
            missing.append("DB_DIR")
        if not self.INCLUDE_FILES:
            missing.append("INCLUDE_FILES")
        if not self.EXCLUDE_FILES:
            missing.append("EXCLUDE_FILES")
        if not self.LOAD_PATTERNS:
            missing.append("LOAD_PATTERNS")
        if not self.PIPELINES:
            missing.append("PIPELINES")

        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}")

    @staticmethod
    def get_config():
        """
        Get the dataset configuration.
        """
        dotenv = CommandUtils.load_dotenv()
        config_path = dotenv.get("DATASET_CONFIG_PATH")
        config = DatasetConfig(config_path)
        config.validate()
        return config
