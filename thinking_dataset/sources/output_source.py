"""Output Source Module."""

__version__ = "0.0.3"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

from dataclasses import dataclass
from .source import Source


@dataclass
class OutputSource(Source):
    """Configuration for output destination."""
    if_exists: str = "replace"  # Default matches config

    def validate(self) -> None:
        """Implement validation logic for OutputSource."""
        if not self.table or not self.column:
            raise ValueError(
                "Both table and column must be provided for OutputSource")

    @classmethod
    def from_config(cls, config: dict) -> 'OutputSource':
        """Create OutputSource from config dictionary."""
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")

        output = cls(table=config.get("table"),
                     column=config.get("column"),
                     if_exists=config.get("if_exists", "replace"))
        output.validate()
        return output
