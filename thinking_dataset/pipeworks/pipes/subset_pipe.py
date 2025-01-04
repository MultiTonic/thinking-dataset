# @file project_root/thinking_dataset/pipeworks/pipes/subset_pipe.py
# @description Defines SubsetPipe for creating subsets of data.
# @version 1.0.0
# @license MIT

import pandas as pd
from .pipe import Pipe
from ...utilities.log import Log


class SubsetPipe(Pipe):
    """
    Pipe to create a subset of data based on specified row and column ranges.
    """

    def flow(self, df: pd.DataFrame, log, **args) -> pd.DataFrame:
        rows = self.config.get("rows")
        columns = self.config.get("columns")

        if not rows and not columns:
            Log.error(
                log,
                "Both rows and columns configurations are missing. One of "
                "each or both must be configured.")
            return df

        Log.info(log, "Starting SubsetPipe")
        if rows:
            Log.info(log, f"Applying row range: {rows}")
            df = df.iloc[rows[0]:rows[1], :]

        if columns and columns != ["all"]:
            Log.info(log, f"Applying column range: {columns}")
            df = df.iloc[:, columns[0]:columns[1]]
        else:
            Log.info(log, "Including all columns")

        total_rows = df.shape[0]
        total_columns = df.shape[1]
        Log.info(log, f"Total rows in subset: {total_rows}")
        Log.info(log, f"Total columns in subset: {total_columns}")

        Log.info(log, "Finished SubsetPipe")
        return df
