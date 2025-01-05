# @file thinking_dataset/io/files.py
# @description Handles file I/O operations for the Thinking Dataset Project.
# @version 1.0.0
# @license MIT

import os
import shutil
from ..utilities.log import Log


class Files:

    def __init__(self, config):
        self.config = config

    @staticmethod
    def exists(path):
        """
        Check if the given path exists.
        """
        return os.path.exists(path)

    def get_raw_path(self):
        base_dir = os.path.join(self.config.root_path, self.config.data_path)
        return os.path.join(base_dir, self.config.raw_path)

    def get_processed_path(self):
        base_dir = os.path.join(self.config.root_path, self.config.data_path)
        return os.path.join(base_dir, self.config.processed_path)

    def make_dir(self, path, log):
        """
        Creates the directory if it doesn't exist.
        """
        full_path = os.path.join(self.config.root_path, path)
        os.makedirs(full_path, exist_ok=True)
        Log.info(log, f"Ensured directory exists: {full_path}")

    @staticmethod
    def remove_dir(path, log):
        """
        Removes the directory if it exists.
        """
        abs_path = os.path.abspath(path)
        if Files.exists(abs_path):
            shutil.rmtree(abs_path)
            Log.info(log, f"Removed directory: {abs_path}")

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
    def format(file, pattern):
        """
        Format the load pattern with the given file's root and extension.
        """
        file_root, file_ext = os.path.splitext(file)
        return pattern.format(file_root=file_root, file_ext=file_ext)
