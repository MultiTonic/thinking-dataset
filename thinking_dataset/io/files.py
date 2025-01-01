"""
@file thinking_dataset/io/files.py
@description Handles file i/o operations for the Thinking Dataset Project.
@version 1.0.0
@license MIT
"""

import os
from ..utilities.log import Log


class Files:

    def __init__(self, raw_dir, processed_dir=None):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir

    def touch(self):
        directories = [self.raw_dir]
        if self.processed_dir:
            directories.append(self.processed_dir)
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    @staticmethod
    def list(dir_path, file_extension=None):
        """
        List files in a directory with an optional file extension filter.
        """
        if file_extension:
            return [
                f for f in os.listdir(dir_path) if f.endswith(file_extension)
            ]
        return os.listdir(dir_path)

    @staticmethod
    def get_path(directory, filename):
        return os.path.join(directory, filename)

    @staticmethod
    def is_excluded(file, excluded_files, log):
        """
        Check if the file is in the excluded files list.
        """
        if file in excluded_files:
            Log.info(log, f"Skipping excluded file: {file}")
            return True
        return False

    @staticmethod
    def get_raw_path(log, root_dir, data_dir, raw_dir):
        base_dir = os.path.join(root_dir, data_dir)
        raw_dir_path = os.path.join(base_dir, raw_dir)
        Log.info(log,
                 f"Data paths: base_dir={base_dir}, raw_dir={raw_dir_path}")
        return raw_dir_path
