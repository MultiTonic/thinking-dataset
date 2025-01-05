"""
@file thinking_dataset/datasets/operations/get_file_list.py
@description Operation to retrieve list of dataset files.
@version 1.0.0
@license MIT
"""

import sys
from .base_operation import BaseOperation
from ...config.config import Config
from ...utilities.log import Log


class GetFileList(BaseOperation):
    """
    A class to retrieve the list of files in the dataset.
    """

    def execute(self):
        try:
            dataset_info = self.data_tonic.get_info.execute(
                f"{self.data_tonic.organization}/{self.data_tonic.dataset}")

            if isinstance(self.config, str):
                self.config = Config(self.config)

            file_list = [
                file.rfilename for file in dataset_info.siblings
                if file.rfilename.endswith(f'.{self.config.dataset_type}')
            ]
            Log.info(self.log, f"Dataset files: {file_list}")
            return file_list
        except Exception as e:
            Log.error(self.log,
                      f"Error retrieving file list: {e}",
                      exc_info=True)
            sys.exit(1)
            return []
