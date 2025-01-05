# @file project_root/thinking_dataset/config/config.py
# @description Defines DatasetConfig class for storing dataset configuration.
# @version 1.0.0
# @license MIT

from ..utilities.command_utils import CommandUtils as Utils
from .config_loader import ConfigLoader as Loader


class Config:
    """
    Class for storing dataset configuration.
    """

    def __init__(self, config_path: str):
        loader = Loader(config_path)
        config = loader.get('config')
        self.HF_DATASET = config.get('hfapi', {}).get('name')
        self.DATASET_TYPE = config.get('hfapi', {}).get('type', 'parquet')

        self.DATABASE_URL = config.get('database', {}).get('url')
        self.database_type = config.get('type', 'sqlite')
        self.pool_size = config.get('pool_size', 5)
        self.max_overflow = config.get('max_overflow', 10)
        self.connect_timeout = config.get('connect_timeout', 30)
        self.read_timeout = config.get('read_timeout', 30)
        self.log_queries = config.get('log_queries', True)
        self.environment = config.get('environment', 'development')

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

        if self.database_type not in ['sqlite', 'postgresql', 'mysql']:
            raise ValueError(
                "Database type must be 'sqlite', 'postgresql', or 'mysql'.")
        if not isinstance(self.pool_size, int) or self.pool_size < 0:
            raise ValueError("Pool size must be a non-negative integer.")
        if not isinstance(self.max_overflow, int) or self.max_overflow < 0:
            raise ValueError("Max overflow must be a non-negative integer.")
        if not isinstance(self.connect_timeout,
                          int) or self.connect_timeout < 0:
            raise ValueError("Connect timeout must be a non-negative integer.")
        if not isinstance(self.read_timeout, int) or self.read_timeout < 0:
            raise ValueError("Read timeout must be a non-negative integer.")
        if not isinstance(self.log_queries, bool):
            raise ValueError("Log queries must be a boolean.")
        if self.environment not in ['development', 'testing', 'production']:
            raise ValueError("Environment must be "
                             "'development', 'testing', or 'production'.")

    @staticmethod
    def get_config():
        dotenv = Utils.load_dotenv()
        config_path = dotenv.get("CONFIG_PATH")
        config = Config(config_path)
        config.validate()
        return config
