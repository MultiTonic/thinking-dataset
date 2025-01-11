# @file thinking_dataset/io/rfile.py
# @description Handles metadata for a single remote file.
# @version 1.0.2
# @license MIT

import datetime


class RFile:

    def __init__(self, name: str, size: int, modified: str):
        self.name = name
        self.size = size
        self.modified = modified

    def __repr__(self):
        if self.modified != "N/A":
            modified_time = datetime.datetime.fromisoformat(
                self.modified).strftime('%m/%d/%Y %I:%M %p')
        else:
            modified_time = self.modified
        return f"{modified_time} {self.size} {self.name}"
