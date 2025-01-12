# @file thinking_dataset/io/rfile.py
# @description Handles metadata for a single remote file.
# @version 1.0.7
# @license MIT

import datetime
import pandas as pd
import os


class RFile:
    _MODIFIED_TIME_FORMAT = '%m/%d/%Y %I:%M %p'

    def __init__(self, name: str, size: int, modified: str = None):
        self.name = name
        self.size = size
        if modified is None:
            self.modified = self.get_now_modified_time()
        else:
            self.modified = modified

    def __repr__(self):
        if self.modified != "N/A":
            modified_time = datetime.datetime.fromisoformat(
                self.modified).strftime(self._MODIFIED_TIME_FORMAT)
        else:
            modified_time = self.modified
        return f"{modified_time} {self.size} {self.name}"

    def get_now_modified_time(self):
        return pd.Timestamp.now().strftime(self._MODIFIED_TIME_FORMAT)

    def get_remote_path(self, base_path: str) -> str:
        relative_path = os.path.relpath(self.name, base_path)
        remote_path = relative_path.replace(os.sep, '/')
        return remote_path
