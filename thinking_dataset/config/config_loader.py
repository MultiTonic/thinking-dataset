"""
@file thinking_dataset/utilities/config_loader.py
@description A class for loading configuration from a YAML file.
@version 1.0.0
@license MIT
"""

import yaml
from typing import Any, Dict


class ConfigLoader:
    """
    A class to load configuration from a YAML file.
    """

    def __init__(self, config_path: str) -> None:
        """
        Initializes the ConfigLoader with the path to the configuration file.
        """
        self.config = self._load(config_path)

    def _load(self, config_path: str) -> Dict[str, Any]:
        """
        Loads the configuration from a YAML file.
        """
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}") from e
        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"Error parsing YAML file: {config_path}") from e

    def get(self, section: str) -> Dict[str, Any]:
        """
        Retrieves a section of the configuration.
        """
        return self.config.get(section, {})
