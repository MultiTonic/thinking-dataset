"""Handle Missing Values Pipeline Module.

This module provides functionality for handling missing values in DataFrames
based on specified column configurations.

Functions:
    None

Classes:
    HandleMissingValuesPipe: Handles missing value operations.
"""

from typing import Any, List, Optional

import pandas as pd

from thinking_dataset.utils.log import Log
from .pipe import Pipe

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class HandleMissingValuesPipe(Pipe):
    """Pipe for handling missing values in DataFrames.

    This pipe:
    1. Validates column specifications
    2. Handles missing value imputation or removal
    3. Provides detailed operation logging

    Config:
        columns (List[str]): Columns to check for missing values
        strategy (str): Strategy for handling missing values ('drop' or 'fill')
        fill_value (Any): Value to use for filling missing values (if strategy
            is 'fill')
    """

    def __init__(self, config: dict) -> None:
        """Initialize missing values handling pipe with configuration.

        Args:
            config (dict): Configuration containing:
                columns (List[str]): Columns to use for missing value handling
                strategy (str): Strategy for handling missing values ('drop'
                    or 'fill')
                fill_value (Any): Value to use for filling missing values (if
                    strategy is 'fill')
        """
        super().__init__(config)
        self.config = config
        self._validate_config(self.config)

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        """Execute the missing values handling pipeline.

        Args:
            df (pd.DataFrame): Input DataFrame
            **args: Additional arguments

        Returns:
            pd.DataFrame: DataFrame with missing values handled

        Raises:
            KeyError: If specified columns are missing
        """
        Log.info("Starting HandleMissingValuesPipe")
        initial_length = len(df)

        columns = self._get_columns(df)
        self._validate_columns(df, columns)

        strategy = self.config.get("strategy", "drop")
        if strategy == "drop":
            df = self._drop_missing_values(df, columns)
        elif strategy == "fill":
            fill_value = self.config.get("fill_value", None)
            df = self._fill_missing_values(df, columns, fill_value)
        else:
            Log.error(f"Unknown strategy: {strategy}")
            raise ValueError(f"Unknown strategy: {strategy}")

        self._log_results(initial_length, len(df))
        Log.info("Finished HandleMissingValuesPipe")
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

        strategy = config.get("strategy", "drop")
        if strategy not in ["drop", "fill"]:
            raise ValueError("Strategy must be 'drop' or 'fill'")

    def _get_columns(self, df: pd.DataFrame) -> List[str]:
        """Get columns to use for missing value handling.

        Args:
            df (pd.DataFrame): Input DataFrame

        Returns:
            List[str]: Columns to check for missing values
        """
        columns = self.config.get("columns", [])
        if "auto" in columns:
            Log.info("Auto-detecting columns for missing value handling")
            return df.columns.tolist()
        return columns

    def _validate_columns(self, df: pd.DataFrame, columns: List[str]) -> None:
        """Validate that required columns exist in DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame
            columns (List[str]): Required columns

        Raises:
            KeyError: If any required columns are missing
        """
        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            Log.warn("Missing columns for "
                     f"missing value handling: {missing_columns}")
            raise KeyError("Missing columns for "
                           f"missing value handling: {missing_columns}")

    @staticmethod
    def _drop_missing_values(df: pd.DataFrame,
                             columns: List[str]) -> pd.DataFrame:
        """Drop rows with missing values in specified columns.

        Args:
            df (pd.DataFrame): Input DataFrame
            columns (List[str]): Columns to check for missing values

        Returns:
            pd.DataFrame: DataFrame with rows dropped
        """
        Log.info(f"Dropping rows with missing values in columns: {columns}")
        return df.dropna(subset=columns)

    @staticmethod
    def _fill_missing_values(df: pd.DataFrame, columns: List[str],
                             fill_value: Any) -> pd.DataFrame:
        """Fill missing values in specified columns with a given value.

        Args:
            df (pd.DataFrame): Input DataFrame
            columns (List[str]): Columns to check for missing values
            fill_value (Any): Value to use for filling missing values

        Returns:
            pd.DataFrame: DataFrame with missing values filled
        """
        Log.info(f"Filling missing values in columns: {columns} "
                 f"with value: {fill_value}")
        return df.fillna({col: fill_value for col in columns})

    @classmethod
    def _log_results(cls, initial_length: int, final_length: int) -> None:
        """Log the results of the missing values handling process.

        Args:
            initial_length (int): Initial number of rows
            final_length (int): Final number of rows
        """
        removed_count = initial_length - final_length
        Log.info(f"Removed {removed_count} rows with missing values")
        Log.info(f"Final number of rows: {final_length}")
