# @file thinking_dataset/config/__init__.py
# @description Inits the config module and makes sub-modules easily importable.
# @version 1.0.9
# @license MIT

from .config_attr import ConfigAttr as Attr
from .config_keys import ConfigKeys as Keys
from .config_loader import ConfigLoader as Loader
from .config_resolver import __get_resolver, __get_dict_resolver
from .config_validator import ConfigValidator as Validator
from .config import Config
from .config_parser import __get_value
from ..utilities.command_utils import CommandUtils as utils

_instance = None
_dotenv = None


def initialize(path=None):
    global _instance, _dotenv
    if _instance is None:
        if path is None:
            _dotenv = utils.load_dotenv()
            path = _dotenv.get("CONFIG_PATH")
        _instance = Config(path)
    return _instance


def get_attr():
    return Attr


def get_keys():
    return Keys


def get_loader():
    return Loader


def get_resolver():
    return __get_resolver


def get_dict_resolver():
    return __get_dict_resolver


def get_validator():
    return Validator


def get_config():
    return Config


def get_parser():
    return __get_value
