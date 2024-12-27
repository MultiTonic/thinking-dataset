"""
@file thinking_dataset/io/files.py
@description Handles file i/o operations for the Thinking Dataset Project.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os


class Files:

    def __init__(self, raw_dir, processed_dir=None):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir

    def ensure_directories(self):
        directories = [self.raw_dir]
        if self.processed_dir:
            directories.append(self.processed_dir)
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def list_files(self, dir_path):
        return os.listdir(dir_path)

    def get_file_path(self, directory, filename):
        return os.path.join(directory, filename)
