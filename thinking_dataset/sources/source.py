"""Base Source Module."""

__version__ = "0.0.3"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Source(ABC):
    """Base configuration for data sources."""
    table: str
    column: str

    @abstractmethod
    def validate(self) -> None:
        """Validate source configuration."""
        if not self.table:
            raise ValueError("Table name is required")
        if not self.column:
            raise ValueError("Column name is required")

    @classmethod
    @abstractmethod
    def from_config(cls, config: dict) -> 'Source':
        """Create Source from config dictionary."""
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")
