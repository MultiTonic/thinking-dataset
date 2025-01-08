"""
@file thinking_dataset/datasets/operations/get_download_size.py
@description Retrieves the download size of the dataset.
@version 1.0.0
@license MIT
"""

from .operation import Operation
from ...utilities.log import Log


class GetDownloadSize(Operation):
    """
    A class to retrieve the download size of the dataset.
    """

    def execute(self):
        """
        Retrieves the download size of the dataset.
        """
        dataset_info = self.data_tonic.get_dataset_info()
        download_size = dataset_info.card_data.get('download_size', 0)
        Log.info(f"Dataset download size: {download_size}")
        return download_size
