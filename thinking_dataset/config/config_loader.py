# @file thinking_dataset/utils/config_loader.py
# @description A class for loading configuration from a YAML file.
# @version 1.0.3
# @license MIT

import yaml
from typing import Any, Dict


class ConfigLoader:
    """
    A class to load configuration from a YAML file.
    """

    def __init__(self, config_path: str) -> None:
        self.config = self._load(config_path)

    def _load(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}") from e
        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"Error parsing YAML file: {config_path}") from e

    def get(self, section: str) -> Dict[str, Any]:
        return self.config.get(section, {})
