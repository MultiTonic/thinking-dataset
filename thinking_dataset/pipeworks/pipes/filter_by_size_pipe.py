"""Size Filter Pipeline Module.

This module provides functionality for filtering DataFrame entries based on
content size thresholds.

Functions:
    None

Classes:
    FilterBySizePipe: Handles content size filtering operations.
"""

from typing import Optional, Tuple

import pandas as pd

from thinking_dataset.utils.log import Log
from thinking_dataset.utils.text_utils import TextUtils
from .pipe import Pipe

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class FilterBySizePipe(Pipe):
    """Pipe for filtering DataFrame entries by content size.

    This pipe:
    1. Validates size threshold configurations
    2. Applies minimum size filtering
    3. Applies maximum size filtering
    4. Tracks memory usage changes
    5. Provides detailed operation logging

    Config:
        column_name (str): Column to check for size
        min_size (int): Minimum content size threshold
        max_size (int): Maximum content size threshold
    """

    def __init__(self, config: dict) -> None:
        """Initialize size filter pipe with configuration.

        Args:
            config (dict): Configuration containing:
                column_name (str): Column to filter
                min_size (int): Minimum size threshold
                max_size (int): Maximum size threshold
        """
        super().__init__(config)
        self._validate_config(self.config)

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        """Execute the size filtering pipeline.

        Args:
            df (pd.DataFrame): Input DataFrame
            **args: Additional arguments

        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        Log.info("Starting FilterBySizePipe")

        config = self._get_config()
        initial_stats = self._get_dataframe_stats(df)

        df = self._apply_size_filters(df, config)

        final_stats = self._get_dataframe_stats(df)
        self._log_results(initial_stats, final_stats, config)

        Log.info("Finished FilterBySizePipe")
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

        if "column_name" not in config:
            raise ValueError("column_name must be specified")

        min_size = config.get("min_size", 0)
        max_size = config.get("max_size", 0)

        if not isinstance(min_size, (int, float)):
            raise ValueError("min_size must be a number")
        if not isinstance(max_size, (int, float)):
            raise ValueError("max_size must be a number")

    @classmethod
    def _get_config(cls) -> dict:
        """Get processing configuration.

        Returns:
            dict: Configuration parameters
        """
        return {
            'column_name': cls.config.get("column_name", "pdf_content"),
            'min_size': cls.config.get("min_size", 0),
            'max_size': cls.config.get("max_size", 0)
        }

    @staticmethod
    def _get_dataframe_stats(df: pd.DataFrame) -> Tuple[int, int]:
        """Get DataFrame statistics.

        Args:
            df (pd.DataFrame): DataFrame to analyze

        Returns:
            Tuple[int, int]: (row_count, memory_usage)
        """
        return len(df), df.memory_usage(deep=True).sum()

    @classmethod
    def _apply_size_filters(cls, df: pd.DataFrame,
                            config: dict) -> pd.DataFrame:
        """Apply size-based filters to DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame
            config (dict): Filter configuration

        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        column = config['column_name']
        min_size = config['min_size']
        max_size = config['max_size']

        if min_size <= 0 and max_size <= 0:
            Log.info("No filtering applied based on size.")
            return df

        if min_size <= 0:
            return df[df[column].apply(lambda x: len(x) <= max_size)]
        if max_size <= 0:
            return df[df[column].apply(lambda x: len(x) >= min_size)]

        return df[df[column].apply(lambda x: min_size <= len(x) <= max_size)]

    @classmethod
    def _log_results(cls, initial: Tuple[int, int], final: Tuple[int, int],
                     config: dict) -> None:
        """Log filtering operation results.

        Args:
            initial (Tuple[int, int]): Initial (rows, memory)
            final (Tuple[int, int]): Final (rows, memory)
            config (dict): Applied configuration
        """
        init_rows, init_mem = initial
        final_rows, final_mem = final

        filtered_count = init_rows - final_rows
        size_reduction = init_mem - final_mem
        reduction_percentage = (size_reduction /
                                init_mem) * 100 if init_mem > 0 else 0

        Log.info(f"Filtering column: {config['column_name']}")
        Log.info(f"Size thresholds - Min: {config['min_size']}, "
                 f"Max: {config['max_size']}")
        Log.info(f"Filtered out {filtered_count} entries based on size")
        Log.info(f"New item count: {final_rows}")

        if reduction_percentage < 1:
            Log.info("Dataset size reduced by: <1%")
        else:
            Log.info(f"Dataset size reduced by: {reduction_percentage:.2f}% "
                     f"({TextUtils.human_readable_size(size_reduction)})")
