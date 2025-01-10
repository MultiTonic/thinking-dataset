# @file thinking_dataset/pipeworks/pipes/subset_pipe.py
# @description Defines SubsetPipe for creating subsets of data.
# @version 1.1.0
# @license MIT

import pandas as pd
from .pipe import Pipe
from thinking_dataset.utils.log import Log


class SubsetPipe(Pipe):
    """
    Pipe to create a subset of data based on specified row and column ranges.
    """

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        rows = self.config.get("rows")
        columns = self.config.get("columns")

        if not rows and not columns:
            Log.error(
                "Both rows and columns configurations are missing. One of "
                "each or both must be configured.")
            return df

        Log.info("Starting SubsetPipe")

        if rows and rows != ["all"]:
            Log.info(f"Applying row range: {rows}")
            df = df.iloc[rows[0]:rows[1], :]
        else:
            Log.info("Including all rows")

        if columns and columns != ["all"]:
            Log.info(f"Applying column range: {columns}")
            df = df.iloc[:, columns[0]:columns[1]]
        else:
            Log.info("Including all columns")

        if 'id' in df.columns:
            df = df[['id'] + [col for col in df.columns if col != 'id']]

        total_rows = df.shape[0]
        total_columns = df.shape[1]
        Log.info(f"Total rows in subset: {total_rows}")
        Log.info(f"Total columns in subset: {total_columns}")
        Log.info("Finished SubsetPipe")

        return df
