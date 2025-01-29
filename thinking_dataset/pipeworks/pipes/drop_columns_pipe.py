"""Drop Columns Pipeline Module.

This module provides functionality for dropping specified columns from
DataFrames.

Functions:
    None

Classes:
    DropColumnsPipe: Handles dropping specified columns from DataFrames.
"""

from typing import Any, Dict, List

import pandas as pd

from thinking_dataset.utils.log import Log
from .pipe import Pipe

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class DropColumnsPipe(Pipe):
    """Pipe to drop specified columns from the DataFrame.

    This pipe:
    1. Validates column specifications
    2. Drops specified columns from the DataFrame
    3. Maintains data integrity during processing

    Config:
        columns (List[str]): Columns to drop
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize drop columns pipe with configuration.

        Args:
            config (Dict[str, Any]): Configuration containing:
                columns (List[str]): Columns to drop
        """
        super().__init__(config)
        self._validate_config(self.config)

    def flow(self, df: pd.DataFrame, **args: Any) -> pd.DataFrame:
        """Execute the drop columns pipeline.

        Args:
            df (pd.DataFrame): Input DataFrame
            **args: Additional arguments

        Returns:
            pd.DataFrame: DataFrame with specified columns dropped
        """
        Log.info("Starting DropColumnsPipe")

        columns = self.config.get("columns", [])

        Log.info(f"Columns to drop: {columns}")

        df = self._drop_columns(df, columns)

        Log.info(f"Dropped columns: {columns}")
        Log.info("Finished DropColumnsPipe")

        return df

    @classmethod
    def _validate_config(cls, config: Dict[str, Any]) -> None:
        """Validate pipe configuration.

        Args:
            config (Dict[str, Any]): Configuration to validate

        Raises:
            ValueError: If configuration is invalid
        """
        if not config:
            return

        columns = config.get("columns", [])
        if not isinstance(columns, list):
            raise ValueError("Columns must be specified as a list")

    @staticmethod
    def _drop_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Drop specified columns from the DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame
            columns (List[str]): Columns to drop

        Returns:
            pd.DataFrame: DataFrame with specified columns dropped
        """
        return df.drop(columns=columns, errors='ignore')
