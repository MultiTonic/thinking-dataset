"""Template Loader Module.

This module provides functionality to load and optionally
validate templates.

Classes:
    TemplateLoader

Functions:
    TemplateLoader.load(path: str, validate: bool) -> str

Exceptions:
    FileNotFoundError
    IOError
"""

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

from functools import lru_cache
from thinking_dataset.templates.template_validator import TemplateValidator


class TemplateLoader:

    @staticmethod
    @lru_cache(maxsize=None)
    def load(path: str, validate: bool = False) -> str:
        """Load a template file from the specified path.

        Args:
            path (str): The path to the template file.
            validate (bool, optional): If True, validate the template
                using TemplateValidator. Defaults to False.

        Returns:
            str: The content of the template file.

        Raises:
            FileNotFoundError: If the template file is not found at
                the specified path.
            IOError: If there is an error reading the template file.
        """
        try:
            with open(path, 'r') as file:
                template = file.read()
                if validate:
                    TemplateValidator.validate(template)
            return template
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {path}")
        except IOError as e:
            raise IOError(f"Error reading template file: {e}")
