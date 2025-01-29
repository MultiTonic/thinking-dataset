"""UV scripts package for Thinking Dataset.

This package contains scripts for managing the project's virtual environment
and package installation using the UV package manager.

Available modules:
    - setup: Creates and configures the virtual environment
    - uninstall: Removes the virtual environment and package
    - theme: Shared console theme configuration
"""

from assets.scripts.uv.theme import console, custom_theme
from assets.scripts.uv.setup import main as setup

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

__all__ = [
    "console",
    "custom_theme",
    "setup",
]
