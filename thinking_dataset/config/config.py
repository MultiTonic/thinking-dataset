# @file thinking_dataset/config/config.py
# @description Defines DatasetConfig class for storing dataset configuration.
# @version 1.0.32
# @license MIT

from thinking_dataset.utils.command_utils import CommandUtils as utils
import thinking_dataset.config as config
import thinking_dataset.config.config_keys as Keys


class Config:
    """
    Singleton class for storing dataset configuration.
    """

    def __new__(cls, *args, **kwargs):
        if not config._instance:
            config._instance = super(Config, cls).__new__(cls)
        return config._instance

    def __init__(self, path: str):
        if hasattr(self, 'initialized'):
            return
        loader = config.get_loader()(path)
        self.config = loader.config

        combined_config = {
            'dataset': self.config.get('dataset', {}),
            'paths': self.config.get('paths', {}),
            'database': self.config.get('database', {}),
            'files': self.config.get('files', {}),
            'pipelines': self.config.get('pipelines', [])
        }

        resolved_config = config.get_dict_resolver()(combined_config,
                                                     combined_config)

        config.get_attr().initialize_attributes(resolved_config, self)
        config.get_validator().validate(self)
        config._dotenv = utils.load_dotenv()
        self.config = resolved_config
        self.paths = resolved_config.get('paths', {})
        self.initialized = True

    @staticmethod
    def get():
        if not config._instance:
            config._dotenv = utils.load_dotenv()
            config_path = config._dotenv.get("CONFIG_PATH")
            config._instance = Config(config_path)
        return config._instance

    @staticmethod
    def get_value(key: Keys):
        config_instance = Config.get()
        value = getattr(config_instance, key.value, None)
        return value

    @staticmethod
    def get_env_value(key: Keys):
        dotenv = config._dotenv
        if dotenv is None:
            dotenv = utils.load_dotenv()
        value = dotenv.get(key.value)
        return value
