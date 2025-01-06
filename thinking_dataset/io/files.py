# @file thinking_dataset/io/files.py
# @description Handles file I/O operations for the Thinking Dataset Project.
# @version 1.0.0
# @license MIT

import os
import shutil
from ..utilities.log import Log
from ..config.config import Config


class Files:

    def __init__(self, config):
        self.config = config

    @staticmethod
    def exists(path):
        return os.path.exists(path)

    def get_raw_path(self):
        base_dir = os.path.join(Config.get_value(self.config, 'root_path'),
                                Config.get_value(self.config, 'data_path'))
        return os.path.join(base_dir, Config.get_value(self.config,
                                                       'raw_path'))

    def get_processed_path(self):
        base_dir = os.path.join(Config.get_value(self.config, 'root_path'),
                                Config.get_value(self.config, 'data_path'))
        processed_path = os.path.join(
            base_dir, Config.get_value(self.config, 'processed_path'))

        if not os.path.exists(processed_path):
            os.makedirs(processed_path)
            Log.info(f"Created processed directory: {processed_path}")

        return processed_path

    def make_dir(self, path):
        root_path = Config.get_value(self.config, 'root_path')
        Log.info(f"root_path: {root_path}")
        full_path = os.path.join(root_path, path)
        os.makedirs(full_path, exist_ok=True)
        Log.info(f"Ensured directory exists: {full_path}")

    @staticmethod
    def remove_dir(path):
        abs_path = os.path.abspath(path)
        if Files.exists(abs_path):
            shutil.rmtree(abs_path)
            Log.info(f"Removed directory: {abs_path}")

    @staticmethod
    def list(dir_path, file_extension=None):
        if file_extension:
            return [
                f for f in os.listdir(dir_path) if f.endswith(file_extension)
            ]
        return os.listdir(dir_path)

    @staticmethod
    def get_path(directory, filename):
        return os.path.join(directory, filename)

    @staticmethod
    def is_excluded(file, excluded_files):
        if file in excluded_files:
            Log.info(f"Skipping excluded file: {file}")
            return True
        return False

    @staticmethod
    def format(file, pattern):
        file_root, file_ext = os.path.splitext(file)
        return pattern.format(file_root=file_root, file_ext=file_ext)
