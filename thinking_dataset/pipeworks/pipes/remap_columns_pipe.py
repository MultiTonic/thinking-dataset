"""Remap Columns Pipeline Module.

This module provides functionality for renaming and reordering DataFrame
columns based on configuration mappings.

Functions:
    None

Classes:
    RemapColumnsPipe: Handles column remapping operations.
"""

from typing import Dict, List, Optional

import pandas as pd

from thinking_dataset.utils.log import Log
from .pipe import Pipe

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class RemapColumnsPipe(Pipe):
    """Pipe for renaming and reordering DataFrame columns.

    This pipe:
    1. Validates column mapping configuration
    2. Renames columns based on mapping dictionary
    3. Reorders columns based on specified order
    4. Provides detailed operation logging

    Config:
        column_mapping (Dict[str, str]): Old to new column name mappings
        column_order (List[str]): Desired order of columns
    """

    def __init__(self, config: dict) -> None:
        """Initialize remap columns pipe with configuration.

        Args:
            config (dict): Configuration containing:
                column_mapping (Dict[str, str]): Column name mappings
                column_order (List[str]): Column order specification
        """
        super().__init__(config)
        self._validate_config()

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        """Execute the column remapping pipeline.

        Args:
            df (pd.DataFrame): Input DataFrame
            **args: Additional arguments

        Returns:
            pd.DataFrame: DataFrame with remapped columns

        Raises:
            ValueError: If configuration is invalid
        """
        Log.info("Starting RemapColumnsPipe")

        column_mapping = self.config.get("column_mapping", {})
        column_order = self.config.get("column_order", [])

        df = self._apply_column_mapping(df, column_mapping)
        df = self._apply_column_order(df, column_order)

        self._log_results(column_mapping, column_order)
        Log.info("Finished RemapColumnsPipe")
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

        mapping = config.get("column_mapping", {})
        order = config.get("column_order", [])

        if not isinstance(mapping, dict):
            raise ValueError("Column mapping must be a dictionary")
        if not isinstance(order, list):
            raise ValueError("Column order must be a list")

    @staticmethod
    def _apply_column_mapping(df: pd.DataFrame,
                              mapping: Dict[str, str]) -> pd.DataFrame:
        """Apply column name mappings to DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame
            mapping (Dict[str, str]): Column name mappings

        Returns:
            pd.DataFrame: DataFrame with renamed columns
        """
        if mapping:
            Log.info(f"Applying column mapping: {mapping}")
            return df.rename(columns=mapping)
        return df

    @staticmethod
    def _apply_column_order(df: pd.DataFrame,
                            order: List[str]) -> pd.DataFrame:
        """Apply column reordering to DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame
            order (List[str]): Desired column order

        Returns:
            pd.DataFrame: DataFrame with reordered columns
        """
        if order:
            Log.info(f"Applying column order: {order}")
            existing_columns = [col for col in order if col in df.columns]
            return df[existing_columns]
        return df

    @staticmethod
    def _log_results(mapping: Dict[str, str], order: List[str]) -> None:
        """Log remapping operation details.

        Args:
            mapping (Dict[str, str]): Applied column mappings
            order (List[str]): Applied column order
        """
        if mapping:
            Log.info(f"Applied {len(mapping)} column renames")
        if order:
            Log.info(f"Reordered {len(order)} columns")
