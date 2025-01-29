"""Theme configuration for UV scripts.

This module defines the custom theme for console output used in UV scripts.
"""

from rich.console import Console
from rich.theme import Theme

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

# Define a custom theme matching UV's color scheme
custom_theme = Theme({
    "command": "bright_cyan",
    "key": "green",
    "text": "white",
    "param": "blue",
    "error": "bold red"
})

# Create a console instance with the custom theme
console = Console(theme=custom_theme)
