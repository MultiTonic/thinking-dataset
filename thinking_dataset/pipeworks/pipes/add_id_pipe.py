# @file thinking_dataset/pipeworks/pipes/add_id_pipe.py
# @description Defines AddIdPipe for adding unique identifiers to rows.
# @version 1.1.0
# @license MIT

import pandas as pd
import uuid
from .pipe import Pipe
from ...utilities.log import Log


class AddIdPipe(Pipe):
    """
    Pipe to add unique identifiers to rows in the DataFrame.
    """

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        Log.info("Starting AddIdPipe")

        id_type = self.config.get("id_type", "int")

        if id_type == "uuid":
            ids = [str(uuid.uuid4()) for _ in range(len(df))]
        else:
            ids = list(range(1, len(df) + 1))

        df.insert(0, 'id', ids)

        Log.info(f"Added unique {id_type} identifiers as the first column.")
        Log.info("Finished AddIdPipe")

        return df
