# @file thinking_dataset/config/config_resolver.py
# @description Defines functions for dynamic variable resolution.
# @version 1.0.35
# @license MIT

import re
from thinking_dataset.config.config_utils import __get_value


def __get_resolver(value, config, max_attempts=3):
    pattern = re.compile(r'\{\{\s*(.*?)\s*\}\}')

    attempts = 0
    while attempts < max_attempts:
        matches = pattern.findall(value)
        if not matches:
            break

        for match in matches:
            try:
                ref_value = __get_value(config, match.strip())
                value = value.replace(f"{{{{{match.strip()}}}}}", ref_value)
            except KeyError:
                raise ValueError(
                    f"Key '{match.strip()}' not found in configuration.")

        if not pattern.findall(value):
            break

        attempts += 1

    if attempts >= max_attempts:
        raise ValueError(
            "Failed to finalize dynamic variable replacement after "
            f"{attempts} attempts for value: '{value}'")

    return value


def __get_dict_resolver(data, config):
    if isinstance(data, dict):
        return {k: __get_dict_resolver(v, config) for k, v in data.items()}
    elif isinstance(data, list):
        return [__get_dict_resolver(v, config) for v in data]
    elif isinstance(data, str):
        return __get_resolver(data, config)
    else:
        return data
