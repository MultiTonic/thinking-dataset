"""
@file thinking_dataset/pipeworks/pipes/remap_columns_pipe.py
@description Defines RemapColumnsPipe for renaming and reordering columns.
@version 1.0.0
@license MIT
"""

import pandas as pd
from .pipe import Pipe
from ...utilities.log import Log


class RemapColumnsPipe(Pipe):
    """
    Pipe to rename and reorder columns in the DataFrame.
    """

    def flow(self, df: pd.DataFrame, log, **args) -> pd.DataFrame:
        column_mapping = self.config.get("column_mapping", {})
        column_order = self.config.get("column_order", [])

        Log.info(log, "Starting RemapColumnsPipe")
        Log.info(log, f"Column mapping: {column_mapping}")
        Log.info(log, f"Column order: {column_order}")

        # Rename columns
        df = df.rename(columns=column_mapping)

        # Reorder columns
        if column_order:
            existing_columns = [
                col for col in column_order if col in df.columns
            ]
            df = df[existing_columns]

        Log.info(log, "Finished RemapColumnsPipe")
        return df
