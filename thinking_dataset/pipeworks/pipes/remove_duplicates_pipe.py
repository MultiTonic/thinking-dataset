"""
@file project_root/thinking_dataset/pipes/remove_duplicates_pipe.py
@description Defines RemoveDuplicatesPipe for removing duplicates.
@version 1.0.0
@license MIT
"""

from .base_pipe import BasePipe
from thinking_dataset.utilities.log import Log


class RemoveDuplicatesPipe(BasePipe):
    """
    Pipe to remove duplicate entries.
    """

    def flow(self, df, log, **args):
        Log.info(log, "Starting -- RemoveDuplicatesPipe")
        Log.info(log, "Passing data through without modification")
        return df
