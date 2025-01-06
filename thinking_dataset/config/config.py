# @file project_root/thinking_dataset/config/config.py
# @description Defines DatasetConfig class for storing dataset configuration.
# @version 1.0.2
# @license MIT

from ..utilities.command_utils import CommandUtils as Utils
from .config_loader import Loader


class Config:
    """
    Class for storing dataset configuration.
    """

    def __init__(self, path: str):
        loader = Loader(path)
        config = loader.get('config')
        self.dataset_name = config.get('huggingface', {}).get('name')
        self.dataset_type = config.get('huggingface',
                                       {}).get('type', 'parquet')
        self.database_url = config.get('database', {}).get('url')
        self.database_type = config.get('database', {}).get('type', 'sqlite')
        self.pool_size = config.get('database', {}).get('pool_size', 5)
        self.max_overflow = config.get('database', {}).get('max_overflow', 10)
        self.connect_timeout = config.get('database',
                                          {}).get('connect_timeout', 30)
        self.read_timeout = config.get('database', {}).get('read_timeout', 30)
        self.log_queries = config.get('database', {}).get('log_queries', True)
        self.environment = config.get('database',
                                      {}).get('environment', 'development')
        self.database_name = config.get('database', {}).get('name')
        self.root_path = config.get('paths', {}).get('root', '.')
        self.data_path = config.get('paths', {}).get('data', 'data')
        self.raw_path = config.get('paths', {}).get('raw', 'raw')
        self.processed_path = config.get('paths',
                                         {}).get('processed', 'processed')
        self.database_path = config.get('paths', {}).get('database', 'db')
        self.include_files = config.get('files', {}).get('include', [])
        self.exclude_files = config.get('files', {}).get('exclude', [])
        self.load_patterns = config.get('files', {}).get(
            'load', ['{file_root}_prepare{file_ext}'])
        self.pipelines = config.get('pipelines', [])

    def validate(self):
        missing = []
        if not self.dataset_name:
            missing.append("dataset_name")
        if not self.dataset_type:
            missing.append("dataset_type")
        if not self.database_url:
            missing.append("database_url")
        if not self.root_path:
            missing.append("root_path")
        if not self.data_path:
            missing.append("data_path")
        if not self.raw_path:
            missing.append("raw_path")
        if not self.processed_path:
            missing.append("processed_path")
        if not self.database_path:
            missing.append("database_path")
        if not self.include_files:
            missing.append("include_files")
        if not self.exclude_files:
            missing.append("exclude_files")
        if not self.load_patterns:
            missing.append("load_patterns")
        if not self.pipelines:
            missing.append("pipelines")

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
    def get():
        dotenv = Utils.load_dotenv()
        config_path = dotenv.get("CONFIG_PATH")
        config = Config(config_path)
        config.validate()
        return config

    @staticmethod
    def get_value(config, key):
        if isinstance(config, dict):
            return config.get(key)
        return getattr(config, key, None)
