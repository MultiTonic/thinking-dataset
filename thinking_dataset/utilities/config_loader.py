"""
@file thinking_dataset/utilities/config_loader.py
@description A class for loading configuration from a YAML file.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import yaml
from typing import Any, Dict


class ConfigLoader:
    """
    A class to load configuration from a YAML file.

    Attributes
    ----------
    config : dict
        The loaded configuration.
    """

    def __init__(self, config_path: str) -> None:
        """
        Initializes the ConfigLoader with the path to the configuration file.

        Parameters
        ----------
        config_path : str
            The path to the configuration file.
        """
        self.config = self._load(config_path)

    def _load(self, config_path: str) -> Dict[str, Any]:
        """
        Loads the configuration from a YAML file.

        Parameters
        ----------
        config_path : str
            The path to the configuration file.

        Returns
        -------
        dict
            The loaded configuration.

        Raises
        ------
        FileNotFoundError
            If the configuration file is not found.
        yaml.YAMLError
            If there is an error parsing the YAML file.
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

        Parameters
        ----------
        section : str
            The section of the configuration to retrieve.

        Returns
        -------
        dict
            The configuration section.
        """
        return self.config.get(section, {})
