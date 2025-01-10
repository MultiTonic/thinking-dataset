# @file thinking_dataset/config/config_utils.py
# @description Utility functions for configuration.
# @version 1.0.1
# @license MIT


def __get_value(config, dot_notation):
    keys = dot_notation.split('.')
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            raise KeyError(f"Key '{key}' not found in configuration.")
    return value