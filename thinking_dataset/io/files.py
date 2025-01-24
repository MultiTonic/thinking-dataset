# @file thinking_dataset/io/files.py
# @description Handles file I/O operations for the Thinking Dataset Project.
# @version 1.2.0
# @license MIT

import os
import shutil
from typing import List

import thinking_dataset.config as conf
from thinking_dataset.config.config_keys import ConfigKeys as Keys
from thinking_dataset.utils.log import Log


class Files:
    """
    Utility class for handling file and directory operations.

    This class:
    1. Manages file system operations across the project.
    2. Handles path resolution and directory creation.
    3. Provides file filtering and pattern matching.
    4. Ensures consistent file handling behavior.

    Methods:
        exists(path): Check if a path exists.
        get_path(key): Get configured path for a given key.
        get_root_path(): Get the project root path.
        get_data_path(): Get the data directory path.
        get_raw_path(): Get the raw data path.
        get_process_path(): Get the processing directory path.
        get_export_path(): Get the export directory path.
        get_database_path(): Get the database directory path.
        make_dir(path): Create a directory if it doesn't exist.
        remove_dir(path): Remove a directory and its contents.
        remove_file(path): Remove a single file.
        list(dir_path, file_extension): List directory contents with optional
            filtering.
        get_file_path(path, file_name): Get full path for a file.
        get_file_name(path): Extract filename from path.
        get_remote_path(remote_path, file_name): Generate remote file path.
        is_excluded(file, excluded_files): Check if file should be excluded.
        format(file, pattern): Format file path according to pattern.
        list_files_recursive(directory, extension): Recursively list files.
        get_dir_name(path): Get directory name from path.
    """

    # Existence checks
    @staticmethod
    def exists(path):
        return os.path.exists(path)

    # File operations
    @staticmethod
    def format(file, pattern):
        file_root, file_ext = os.path.splitext(file)
        file_name = os.path.basename(file)
        return pattern.format(file_root=file_root,
                              file_ext=file_ext,
                              file_name=file_name)

    @staticmethod
    def get_dir_name(path):
        return os.path.dirname(path)

    @staticmethod
    def get_file_name(path):
        return os.path.basename(path)

    @staticmethod
    def get_file_path(path, file_name):
        return os.path.normpath(os.path.join(path, file_name))

    @staticmethod
    def get_remote_path(remote_path, file_name):
        return f"{remote_path}/{file_name}".replace(os.sep, '/')

    # Directory operations
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

    # Path getters
    @staticmethod
    def get_data_path():
        return Files.get_path(Keys.DATA_PATH)

    @staticmethod
    def get_database_path():
        return Files.get_path(Keys.DATABASE_PATH)

    @staticmethod
    def get_export_path():
        return Files.get_path(Keys.EXPORT_PATH)

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
    def get_process_path():
        return Files.get_path(Keys.PROCESS_PATH)

    @staticmethod
    def get_raw_path():
        return Files.get_path(Keys.RAW_PATH)

    @staticmethod
    def get_root_path():
        return Files.get_path(Keys.ROOT_PATH)

    # List and filter operations
    @staticmethod
    def is_excluded(file, excluded_files):
        if file in excluded_files:
            Log.info(f"Skipping excluded file: {file}")
            return True
        return False

    @staticmethod
    def list(dir_path, file_extension=None):
        if file_extension:
            return [
                f for f in os.listdir(dir_path) if f.endswith(file_extension)
            ]
        return os.listdir(dir_path)

    @staticmethod
    def list_files_recursive(directory: str,
                             extension: str = None) -> List[str]:
        file_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                if extension is None or file.endswith(extension):
                    file_paths.append(Files.get_file_path(root, file))
        return file_paths
