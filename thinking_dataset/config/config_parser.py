# @file thinking_dataset/utilities/config_parser.py
# @description Utility function to handle dot notation lookup.
# @version 1.0.8
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
