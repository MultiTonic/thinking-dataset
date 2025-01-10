# @file config.py
# @description Defines DatasetConfig class for storing dataset configuration.
# @version 1.0.36
# @license MIT

from thinking_dataset.utils.command_utils import CommandUtils as utils
import thinking_dataset.config as conf
import thinking_dataset.config.config_keys as Keys


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

        combined_config = {
            'dataset': self.config.get('dataset', {}),
            'paths': self.config.get('paths', {}),
            'database': self.config.get('database', {}),
            'files': self.config.get('files', {}),
            'pipelines': self.config.get('pipelines', [])
        }

        resolved_config = conf.get_dict_resolver()(combined_config,
                                                   combined_config)

        conf.get_attr().initialize_attributes(resolved_config, self)
        conf.get_validator().validate(self)
        conf._dotenv = utils.load_dotenv()
        self.config = resolved_config
        self.paths = resolved_config.get('paths', {})
        self.initialized = True

    @staticmethod
    def get():
        if not conf._instance:
            conf._dotenv = utils.load_dotenv()
            config_path = conf._dotenv.get("CONFIG_PATH")
            conf._instance = Config(config_path)
        return conf._instance

    def get_value(self, key):
        if isinstance(key, Keys.ConfigKeys):
            key = key.value
        value = getattr(self, key, None)
        return value

    @staticmethod
    def get_env_value(key):
        if isinstance(key, Keys.ConfigKeys):
            key = key.value
        dotenv = conf._dotenv
        if dotenv is None:
            dotenv = utils.load_dotenv()
        value = dotenv.get(key)
        return value
