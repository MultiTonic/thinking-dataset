# @file thinking_dataset/config/config.py
# @description Defines DatasetConfig class for storing dataset configuration.
# @version 1.0.4
# @license MIT

from ..utilities.log import Log
from .config_keys import ConfigKeys as Keys
from .config_loader import ConfigLoader as Loader
from .config_validator import ConfigValidator as Validator
from ..utilities.command_utils import CommandUtils as Utils


class Config:
    """
    Singleton class for storing dataset configuration.
    """
    _instance = None
    _dotenv = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, path: str):
        if hasattr(self, 'initialized'):
            return
        Log.info(f"Initializing Config with path: {path}")
        loader = Loader(path)
        config = loader.get('config')
        Log.info(f"Loaded config: {config}")
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
        self.root = config.get('paths', {}).get('root', '.')
        self.data = config.get('paths', {}).get('data', './data')
        self.raw = config.get('paths', {}).get('raw', './data/raw')
        self.process = config.get('paths', {}).get('process', './data/process')
        self.export = config.get('paths', {}).get('export', './data/export')
        self.database = config.get('paths', {}).get('database', './data/db')
        self.include_files = config.get('files', {}).get('include', [])
        self.exclude_files = config.get('files', {}).get('exclude', [])
        self.load_patterns = config.get('files', {}).get(
            'load', ['{file_root}_prepare{file_ext}'])
        self.pipelines = config.get('pipelines', [])

        Validator.validate(self)
        Config._dotenv = Utils.load_dotenv()
        self.initialized = True
        Log.info("Config initialization complete.")

    @staticmethod
    def get():
        if not Config._instance:
            dotenv = Utils.load_dotenv()
            config_path = dotenv.get("CONFIG_PATH")
            Config._instance = Config(config_path)
        return Config._instance

    @staticmethod
    def get_value(key: Keys):
        config = Config.get()
        Log.info(f"Retrieving config value for key: {key}")
        value = getattr(config, key.value, None)
        Log.info(f"Config value for key '{key}': {value}")
        return value

    @staticmethod
    def get_env_value(key: Keys):
        dotenv = Config.get()._dotenv
        value = dotenv.get(key.value)
        Log.info(f"Environment variable value for key '{key}': {value}")
        return value
