"""Input Source Module."""

__version__ = "0.0.3"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

import random
from dataclasses import dataclass
from typing import List, Any

import pandas as pd
from sqlalchemy import MetaData, Table, select
from .source import Source


@dataclass
class InputSource(Source):
    """Configuration and handling for an input source."""
    label: str
    amount: int = 1
    length: int = 0  # 0 means no truncation
    offset: int = 0
    ellipsis: str = ""  # Empty string means no ellipsis
    shuffle: bool = False

    def validate(self) -> None:
        """Validate input source configuration."""
        super().validate()
        if not self.label:
            raise ValueError("Label is required")
        if self.amount < 1:
            raise ValueError("Amount must be at least 1")
        if self.length < 0:
            raise ValueError("Length cannot be negative")
        if self.offset < 0:
            raise ValueError("Offset cannot be negative")
        if self.length > 0 and self.offset >= self.length:
            raise ValueError(f"Offset ({self.offset}) cannot be greater than "
                             f"length ({self.length})")

    def fetch_source(self, session: Any) -> pd.DataFrame:
        """Fetch source texts from database table."""
        table = Table(self.table, MetaData(), autoload_with=session.bind)
        return pd.read_sql(select(table.c[self.column]), session.bind)

    def shuffle_samples(self, source: pd.DataFrame) -> pd.DataFrame:
        """Shuffle the source data if enabled."""
        if self.shuffle:
            return source.sample(frac=1).reset_index(drop=True)
        return source

    def get_samples(self,
                    source: pd.DataFrame,
                    ellipsis: str = "") -> List[str]:
        """Get random samples from source data."""
        if source.empty:
            raise ValueError(
                f"No source data available for label {self.label}")

        source = self.shuffle_samples(source)
        indices = random.sample(range(len(source)), self.amount)
        samples = []

        for idx in indices:
            full_text = source.iloc[idx].values[0]
            if self.length > 0:
                # Account for ellipsis length in sample size
                actual_length = self.length
                if ellipsis:
                    actual_length = max(0, self.length - len(ellipsis))
                sample = full_text[self.offset:self.offset + actual_length]
                if ellipsis and len(full_text[self.offset:]) > actual_length:
                    sample = sample + ellipsis
            else:
                sample = full_text
            samples.append(sample)

        return samples

    @classmethod
    def from_config(cls, config: dict) -> 'InputSource':
        """Create InputSource from config dictionary."""
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")

        source = cls(table=config.get("table"),
                     column=config.get("column"),
                     label=config.get("label", "seeds"),
                     amount=config.get("amount", 1),
                     length=config.get("length", 0),
                     offset=config.get("offset", 0),
                     ellipsis=config.get("ellipsis", ""),
                     shuffle=config.get("shuffle", False))
        source.validate()
        return source
