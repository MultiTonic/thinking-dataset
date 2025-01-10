# @file thinking_dataset/config/__init__.py
# @description Inits the config module and makes sub-modules easily importable.
# @version 1.1.9
# @license MIT

from .config_attr import ConfigAttr as Attr
from .config_keys import ConfigKeys as Keys
from .config_loader import ConfigLoader as Loader
from .config_resolver import __get_resolver, __get_dict_resolver
from .config_validator import ConfigValidator as Validator
from .config import Config
from .config_parser import __get_value
from thinking_dataset.utils.command_utils import CommandUtils as utils
from thinking_dataset.utils.log import Log

_instance = None
_dotenv = None


def initialize(path=None):
    global _instance, _dotenv
    if (_instance is None):
        if path is None:
            _dotenv = utils.load_dotenv()
            path = _dotenv.get("CONFIG_PATH", None)
            if not path:
                Log.error("CONFIG_PATH is not set or retrieved as None.")
                raise ValueError(
                    "CONFIG_PATH is not set in the environment variables.")
        _instance = Config(path)
    return _instance


def get_value(key):
    if not _instance:
        raise ValueError("Config instance is not initialized.")
    return _instance.get_value(key)


def get_env_value(key):
    if not _instance:
        raise ValueError("Config instance is not initialized.")
    return _instance.get_env_value(key)


def get_loader():
    return Loader


def get_attr():
    return Attr


def get_keys():
    return Keys


def get_validator():
    return Validator


def get_resolver():
    return __get_resolver


def get_value_wrapper():
    return __get_value


def get_dict_resolver():
    return __get_dict_resolver


__all__ = [
    "initialize",
    "get_attr",
    "get_keys",
    "get_loader",
    "get_dict_resolver",
    "get_validator",
    "get_config",
    "get_value",
    "get_env_value",
    "get_resolver",
    "get_value_wrapper",
]
