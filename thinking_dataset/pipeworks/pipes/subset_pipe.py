"""Subset Pipeline Module.

This module provides functionality for creating data subsets by selecting
specific rows and columns from input DataFrames based on configuration.

Functions:
    None

Classes:
    SubsetPipe: Handles data subsetting operations.
"""

from typing import List, Optional, Union

import pandas as pd

from thinking_dataset.utils.log import Log
from .pipe import Pipe

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class SubsetPipe(Pipe):
    """Pipe for creating configurable data subsets.

    This pipe:
    1. Validates input DataFrame structure
    2. Applies configured row range filters
    3. Applies configured column range filters
    4. Maintains ID column positioning
    5. Provides detailed operation logging

    Config:
        rows (List[int]): Start and end indices for row selection
        columns (List[int]): Start and end indices for column selection
    """

    def __init__(self, config: dict) -> None:
        """Initialize subset pipe with configuration.

        Args:
            config (dict): Configuration containing:
                rows (List[int]): Row range [start, end]
                columns (List[int]): Column range [start, end]
        """
        super().__init__(config)
        self._validate_config(config)

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        """Execute the subsetting pipeline.

        Args:
            df (pd.DataFrame): Input DataFrame
            **args: Additional arguments

        Returns:
            pd.DataFrame: Subset DataFrame

        Raises:
            ValueError: If configuration is invalid
        """
        Log.info("Starting SubsetPipe")

        rows = self.config.get("rows")
        columns = self.config.get("columns")

        if not self._has_valid_ranges(rows, columns):
            Log.error("Both rows and columns configurations are missing. "
                      "One or both must be configured.")
            return df

        df = self._apply_row_filter(df, rows)
        df = self._apply_column_filter(df, columns)
        df = self._reorder_columns(df)

        self._log_results(df)
        Log.info("Finished SubsetPipe")
        return df

    @classmethod
    def _validate_config(cls, config: dict) -> None:
        """Validate pipe configuration.

        Args:
            config (dict): Configuration to validate

        Raises:
            ValueError: If configuration is invalid
        """
        if not config:
            raise ValueError("Empty subset configuration")

        rows = config.get("rows", [])
        columns = config.get("columns", [])

        if rows and rows != ["all"] and len(rows) != 2:
            raise ValueError("Row range must be [start, end]")
        if columns and columns != ["all"] and len(columns) != 2:
            raise ValueError("Column range must be [start, end]")

    @staticmethod
    def _has_valid_ranges(rows: Optional[List[int]],
                          columns: Optional[List[int]]) -> bool:
        """Check if valid range configurations exist.

        Args:
            rows (Optional[List[int]]): Row range configuration
            columns (Optional[List[int]]): Column range configuration

        Returns:
            bool: True if at least one valid range exists
        """
        return bool(rows or columns)

    @staticmethod
    def _apply_row_filter(
            df: pd.DataFrame,
            rows: Optional[List[Union[int, str]]]) -> pd.DataFrame:
        """Apply row range filter to DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame
            rows (Optional[List[Union[int, str]]]): Row range or ["all"]

        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        if rows and rows != ["all"]:
            Log.info(f"Applying row range: {rows}")
            df = df.iloc[rows[0]:rows[1], :]
        else:
            Log.info("Including all rows")
        return df

    @staticmethod
    def _apply_column_filter(
            df: pd.DataFrame,
            columns: Optional[List[Union[int, str]]]) -> pd.DataFrame:
        """Apply column range filter to DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame
            columns (Optional[List[Union[int, str]]]): Column range or ["all"]

        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        if columns and columns != ["all"]:
            Log.info(f"Applying column range: {columns}")
            df = df.iloc[:, columns[0]:columns[1]]
        else:
            Log.info("Including all columns")
        return df

    @staticmethod
    def _reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Ensure ID column is first if present.

        Args:
            df (pd.DataFrame): Input DataFrame

        Returns:
            pd.DataFrame: DataFrame with reordered columns
        """
        if 'id' in df.columns:
            cols = ['id'] + [col for col in df.columns if col != 'id']
            return df[cols]
        return df

    @classmethod
    def _log_results(cls, df: pd.DataFrame) -> None:
        """Log subset operation results.

        Args:
            df (pd.DataFrame): Resulting DataFrame
        """
        total_rows, total_columns = df.shape
        Log.info(f"Total rows in subset: {total_rows}")
        Log.info(f"Total columns in subset: {total_columns}")
