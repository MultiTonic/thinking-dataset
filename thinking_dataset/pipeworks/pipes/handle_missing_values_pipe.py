"""
@file project_root/thinking_dataset/pipes/handle_missing_values_pipe.py
@description Defines HandleMissingValuesPipe for handling missing values.
@version 1.0.0
@license MIT
"""

from .base_pipe import BasePipe
from thinking_dataset.utilities.log import Log


class HandleMissingValuesPipe(BasePipe):
    """
    Pipe to handle missing values.
    """

    def flow(self, df, log, **args):
        Log.info(log, "Starting HandleMissingValuesPipe")
        Log.info(log, "Passing data through without modification")
        return df
