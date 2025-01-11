# @file thinking_dataset/config/config.py
# @description Defines DatasetConfig class for storing dataset configuration.
# @version 1.0.39
# @license MIT

import thinking_dataset.config as conf
import thinking_dataset.config.config_keys as Keys
from thinking_dataset.utils.command_utils import CommandUtils as utils

CK = Keys.ConfigKeys


class Config:
    """
    Singleton class for storing dataset configuration.
    """

    def __new__(cls, *args, **kwargs):
        if not conf._instance:
            conf._instance = super(Config, cls).__new__(cls)
        return conf._instance

    def __init__(self, path: str):
        if hasattr(self, 'initialized'):
            return

        loader = conf.get_loader()(path)
        self.config = loader.config

        config = {
            'dataset': self.config.get('dataset', {}),
            'paths': self.config.get('paths', {}),
            'database': self.config.get('database', {}),
            'files': self.config.get('files', {}),
            'pipelines': self.config.get('pipelines', [])
        }

        config = conf.get_dict_resolver()(config, config)

        conf.get_attr().initialize_attributes(config, self)
        conf.get_validator().validate(self)
        conf._dotenv = utils.load_dotenv()
        self.config = config
        self.paths = config.get('paths', {})

        self.initialized = True

    @staticmethod
    def get():
        if not conf._instance:
            conf._dotenv = utils.load_dotenv()
            path = conf._dotenv.get("CONFIG_PATH")
            conf._instance = Config(path)
        return conf._instance

    def get_value(self, key):
        if isinstance(key, CK):
            key = key.value
        value = getattr(self, key, None)
        return value

    @staticmethod
    def get_env_value(key):
        if isinstance(key, CK):
            key = key.value
        dotenv = conf._dotenv
        if dotenv is None:
            dotenv = utils.load_dotenv()
        value = dotenv.get(key)
        return value
