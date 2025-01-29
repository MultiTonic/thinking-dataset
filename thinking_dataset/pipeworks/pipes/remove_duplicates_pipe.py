"""Remove Duplicates Pipeline Module.

This module provides functionality for removing duplicate rows from DataFrames
based on specified column combinations.

Functions:
    None

Classes:
    RemoveDuplicatesPipe: Handles duplicate row removal operations.
"""

from typing import List, Optional

import pandas as pd

from thinking_dataset.utils.log import Log
from .pipe import Pipe

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class RemoveDuplicatesPipe(Pipe):
    """Pipe for removing duplicate rows from DataFrames.

    This pipe:
    1. Validates column specifications
    2. Handles automatic column detection
    3. Removes duplicate rows based on specified columns
    4. Provides detailed operation logging

    Config:
        columns (List[str]): Columns to check for duplicates
    """

    def __init__(self, config: dict) -> None:
        """Initialize duplicate removal pipe with configuration.

        Args:
            config (dict): Configuration containing:
                columns (List[str]): Columns to use for duplicate detection
        """
        super().__init__(config)
        self._validate_config(self.config)

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        """Execute the duplicate removal pipeline.

        Args:
            df (pd.DataFrame): Input DataFrame
            **args: Additional arguments

        Returns:
            pd.DataFrame: DataFrame with duplicates removed

        Raises:
            KeyError: If specified columns are missing
        """
        Log.info("Starting RemoveDuplicatesPipe")
        initial_length = len(df)

        columns = self._get_columns(df)
        self._validate_columns(df, columns)

        if not columns:
            Log.warn("No columns specified for duplicate check. "
                     "Skipping duplicate removal.")
            return df

        df = self._remove_duplicates(df, columns)

        self._log_results(initial_length, len(df))
        Log.info("Finished RemoveDuplicatesPipe")
        return df

    @classmethod
    def _validate_config(cls, config: Optional[dict] = None) -> None:
        """Validate pipe configuration.

        Args:
            config (Optional[dict]): Configuration to validate

        Raises:
            ValueError: If configuration is invalid
        """
        if not config:
            return

        columns = config.get("columns", [])
        if not isinstance(columns, list):
            raise ValueError("Columns must be specified as a list")

    @classmethod
    def _get_columns(cls, df: pd.DataFrame) -> List[str]:
        """Get columns to use for duplicate detection.

        Args:
            df (pd.DataFrame): Input DataFrame

        Returns:
            List[str]: Columns to check for duplicates
        """
        columns = cls.pipeline_config.get("columns", [])
        if "auto" in columns:
            Log.info("Auto-detecting columns for duplicate check")
            return df.columns.tolist()
        return columns

    @classmethod
    def _validate_columns(cls, df: pd.DataFrame, columns: List[str]) -> None:
        """Validate that required columns exist in DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame
            columns (List[str]): Required columns

        Raises:
            KeyError: If any required columns are missing
        """
        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            Log.warn(f"Missing columns for duplicate check: {missing_columns}")
            raise KeyError(
                f"Missing columns for duplicate check: {missing_columns}")

    @staticmethod
    def _remove_duplicates(df: pd.DataFrame,
                           columns: List[str]) -> pd.DataFrame:
        """Remove duplicate rows from DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame
            columns (List[str]): Columns to check for duplicates

        Returns:
            pd.DataFrame: DataFrame with duplicates removed
        """
        Log.info(f"Checking columns for duplicates: {columns}")
        return df.drop_duplicates(subset=columns)

    @classmethod
    def _log_results(cls, initial_length: int, final_length: int) -> None:
        """Log the results of the duplicate removal process.

        Args:
            initial_length (int): Initial number of rows
            final_length (int): Final number of rows
        """
        removed_count = initial_length - final_length
        Log.info(f"Removed {removed_count} duplicates")
        Log.info(f"Final number of rows: {final_length}")
