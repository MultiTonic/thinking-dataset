# @file thinking_dataset/io/files.py
# @description Handles file I/O operations for the Thinking Dataset Project.
# @version 1.1.8
# @license MIT

import os
import shutil
from thinking_dataset.utils.log import Log
import thinking_dataset.config as conf
from thinking_dataset.config.config_keys import ConfigKeys as Keys
from typing import List


class Files:

    @staticmethod
    def exists(path):
        return os.path.exists(path)

    @staticmethod
    def get_path(key: Keys):
        instance = conf.initialize()
        path = instance.get_value(key)
        Log.info(f"Retrieved directory for key {key}: {path}")
        if path is None:
            raise ValueError(
                f"Configuration key '{key.value}' is missing or None.")
        Files.make_dir(path)
        return path

    @staticmethod
    def get_root_path():
        return Files.get_path(Keys.ROOT_PATH)

    @staticmethod
    def get_data_path():
        return Files.get_path(Keys.DATA_PATH)

    @staticmethod
    def get_raw_path():
        return Files.get_path(Keys.RAW_PATH)

    @staticmethod
    def get_process_path():
        return Files.get_path(Keys.PROCESS_PATH)

    @staticmethod
    def get_export_path():
        return Files.get_path(Keys.EXPORT_PATH)

    @staticmethod
    def get_database_path():
        return Files.get_path(Keys.DATABASE_PATH)

    @staticmethod
    def make_dir(path):
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def remove_dir(path):
        abs_path = os.path.abspath(path)
        if Files.exists(abs_path):
            shutil.rmtree(abs_path)

    @staticmethod
    def remove_file(path):
        if Files.exists(path):
            os.remove(path)

    @staticmethod
    def list(dir_path, file_extension=None):
        if file_extension:
            return [
                f for f in os.listdir(dir_path) if f.endswith(file_extension)
            ]
        return os.listdir(dir_path)

    @staticmethod
    def get_file_path(path, file_name):
        return os.path.normpath(os.path.join(path, file_name))

    @staticmethod
    def get_file_name(path):
        return os.path.basename(path)

    @staticmethod
    def get_remote_path(remote_path, file_name):
        return f"{remote_path}/{file_name}".replace(os.sep, '/')

    @staticmethod
    def is_excluded(file, excluded_files):
        if file in excluded_files:
            Log.info(f"Skipping excluded file: {file}")
            return True
        return False

    @staticmethod
    def format(file, pattern):
        file_root, file_ext = os.path.splitext(file)
        file_name = os.path.basename(file)
        return pattern.format(file_root=file_root,
                              file_ext=file_ext,
                              file_name=file_name)

    @staticmethod
    def list_files_recursive(directory: str,
                             extension: str = None) -> List[str]:
        file_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                if extension is None or file.endswith(extension):
                    file_paths.append(Files.get_file_path(root, file))
        return file_paths
