"""
@file thinking_dataset/pipeworks/pipes/add_id_pipe.py
@description Defines AddIdPipe for adding unique identifiers to rows.
@version 1.0.0
@license MIT
"""

import pandas as pd
import uuid
from .pipe import Pipe
from ...utilities.log import Log


class AddIdPipe(Pipe):
    """
    Pipe to add unique identifiers to rows in the DataFrame.
    """

    def flow(self, df: pd.DataFrame, log, **args) -> pd.DataFrame:
        Log.info(log, "Starting AddIdPipe")

        # Generate unique IDs and insert as the first column
        ids = [str(uuid.uuid4()) for _ in range(len(df))]
        df.insert(0, 'id', ids)

        Log.info(log, "Added unique identifiers as the first column.")
        Log.info(log, "Finished AddIdPipe")

        return df
