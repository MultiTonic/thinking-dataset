"""
@file thinking_dataset/pipeworks/pipes/clean_whitespace_pipe.py
@description Defines CleanWhitespacePipe for cleaning unnecessary whitespace.
@version 1.0.0
@license MIT
"""

import pandas as pd
import re
from tqdm import tqdm
from .pipe import Pipe
from ...utilities.log import Log


class CleanWhitespacePipe(Pipe):
    """
    Pipe to clean unnecessary whitespace from text columns.
    """

    def flow(self, df: pd.DataFrame, log, **args) -> pd.DataFrame:
        columns = self.config.get("columns", [])

        # Support for auto-detection of columns
        if columns == ["auto"]:
            columns = df.columns.tolist()

        Log.info(log, "Starting CleanWhitespacePipe")
        Log.info(log, f"Columns to clean: {columns}")

        initial_lengths = df[columns].map(len)

        def clean_text(content):
            content = re.sub(r'\s+', ' ', content)
            content = content.strip()
            return content

        for col in columns:
            Log.info(log, f"Cleaning column: {col}")
            tqdm.pandas(desc=f"Cleaning {col}")
            df[col] = df[col].progress_apply(clean_text)

        final_lengths = df[columns].map(len)
        total_initial_length = initial_lengths.sum().sum()
        total_final_length = final_lengths.sum().sum()
        reduction_percentage = ((total_initial_length - total_final_length) /
                                total_initial_length) * 100

        Log.info(log, "Finished CleanWhitespacePipe")
        Log.info(log, f"Whitespace reduced by: {reduction_percentage:.2f}%")

        return df
