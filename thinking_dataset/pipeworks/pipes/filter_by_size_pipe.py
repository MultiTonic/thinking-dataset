"""
@file thinking_dataset/pipeworks/pipes/filter_by_size_pipe.py
@description Defines FilterBySizePipe for dropping entries based on size.
@version 1.0.0
@license MIT
"""

import pandas as pd
from .pipe import Pipe
from ...utilities.log import Log
from ...utilities.text_utils import TextUtils


class FilterBySizePipe(Pipe):
    """
    Pipe to filter out entries based on size.
    """

    def flow(self, df: pd.DataFrame, log, **args) -> pd.DataFrame:
        column_name = self.config.get("column_name", "pdf_content")
        min_size = self.config.get("min_size", 0)
        max_size = self.config.get("max_size", 0)

        Log.info(log, "Starting FilterBySizePipe")
        Log.info(log, f"Filtering column: {column_name}")
        Log.info(log, f"Minimum size threshold: {min_size}")
        Log.info(log, f"Maximum size threshold: {max_size}")

        original_length = len(df)
        original_size = df.memory_usage(deep=True).sum()

        if min_size <= 0 and max_size <= 0:
            Log.info(log, "No filtering applied based on size.")
        elif min_size <= 0:
            df = df[df[column_name].apply(lambda x: len(x) <= max_size)]
        elif max_size <= 0:
            df = df[df[column_name].apply(lambda x: len(x) >= min_size)]
        else:
            df = df[df[column_name].apply(
                lambda x: min_size <= len(x) <= max_size)]

        filtered_length = len(df)
        filtered_size = df.memory_usage(deep=True).sum()
        size_reduction = original_size - filtered_size
        reduction_percentage = (size_reduction / original_size) * 100

        Log.info(
            log, f"Filtered out {original_length - filtered_length} "
            "entries based on size.")
        Log.info(log, f"New item count: {filtered_length})")
        if reduction_percentage < 1:
            Log.info(log, "Dataset size reduced by: <1%")
        else:
            Log.info(
                log, f"Dataset size reduced by: {reduction_percentage:.2f}% "
                f"({TextUtils.human_readable_size(size_reduction)})")
        Log.info(log, "Finished FilterBySizePipe")

        return df
