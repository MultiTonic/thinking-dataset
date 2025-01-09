# @file thinking_dataset/config/config.py
# @description Defines DatasetConfig class for storing dataset configuration.
# @version 1.0.33
# @license MIT

from ..utilities.command_utils import CommandUtils as utils
import thinking_dataset.config as cfg
from thinking_dataset.config.config_keys import ConfigKeys as Keys


class Config:
    """
    Singleton class for storing dataset configuration.
    """

    def __new__(cls, *args, **kwargs):
        if not cfg._instance:
            cfg._instance = super(Config, cls).__new__(cls)
        return cfg._instance

    def __init__(self, path: str):
        if hasattr(self, 'initialized'):
            return
        loader = cfg.get_loader()(path)
        self.config = loader.config

        combined_config = {
            'dataset': self.config.get('dataset', {}),
            'paths': self.config.get('paths', {}),
            'database': self.config.get('database', {}),
            'files': self.config.get('files', {}),
            'pipelines': self.config.get('pipelines', [])
        }

        resolved_config = cfg.get_dict_resolver()(combined_config,
                                                  combined_config)

        cfg.get_attr().initialize_attributes(resolved_config, self)
        cfg.get_validator().validate(self)
        cfg._dotenv = utils.load_dotenv()
        self.config = resolved_config
        self.paths = resolved_config.get('paths', {})
        self.initialized = True

    @staticmethod
    def get():
        if not cfg._instance:
            cfg._dotenv = utils.load_dotenv()
            config_path = cfg._dotenv.get("CONFIG_PATH")
            cfg._instance = Config(config_path)
        return cfg._instance

    def get_value(self, key: Keys):
        value = getattr(self, key.value, None)
        return value

    @staticmethod
    def get_env_value(key: Keys):
        dotenv = cfg._dotenv
        if dotenv is None:
            dotenv = utils.load_dotenv()
        value = dotenv.get(key.value)
        return value
