"""
@file project_root/thinking_dataset/pipes/remove_duplicates_pipe.py
@description Defines RemoveDuplicatesPipe for removing duplicates.
@version 1.0.0
@license MIT
"""

import pandas as pd
from .pipe import Pipe
from ...utilities.log import Log


class RemoveDuplicatesPipe(Pipe):
    """
    Pipe to remove duplicates from the DataFrame.
    """

    def flow(self, df: pd.DataFrame, log, **args) -> pd.DataFrame:
        columns = self.config.get("columns")
        initial_length = len(df)

        if "auto" in columns:
            Log.info(log, "Auto-detecting columns for duplicate check")
            columns = df.columns.tolist()

        Log.info(log, "Starting RemoveDuplicatesPipe")
        Log.info(log, f"Initial number of rows: {initial_length}")
        Log.info(log, f"Columns to check for duplicates: {columns}")

        # Check if required columns are present in the DataFrame
        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            Log.error(
                log, f"Missing columns for duplicate check: {missing_columns}")
            raise KeyError(
                f"Missing columns for duplicate check: {missing_columns}")

        df = df.drop_duplicates(subset=columns)

        final_length = len(df)
        removed_count = initial_length - final_length

        Log.info(log, f"Removed {removed_count} duplicates")
        Log.info(log, f"Final number of rows: {final_length}")
        Log.info(log, "Finished RemoveDuplicatesPipe")

        return df
