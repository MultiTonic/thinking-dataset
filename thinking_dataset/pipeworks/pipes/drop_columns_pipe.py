# @file thinking_dataset/pipeworks/pipes/drop_columns_pipe.py
# @description Defines DropColumnsPipe for dropping specified columns.
# @version 1.0.0
# @license MIT

import pandas as pd
from .pipe import Pipe
from ...utilities.log import Log


class DropColumnsPipe(Pipe):
    """
    Pipe to drop specified columns from the DataFrame.
    """

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        columns = self.config.get("columns", [])

        Log.info("Starting DropColumnsPipe")
        Log.info(f"Columns to drop: {columns}")

        df = df.drop(columns=columns, errors='ignore')

        Log.info(f"Dropped columns: {columns}")
        Log.info("Finished DropColumnsPipe")

        return df
