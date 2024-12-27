"""
@file get_download_size.py
@description Retrieves the download size of the dataset.
@version 1.0.0
@license MIT
@author Kara
"""

from .base_operation import BaseOperation


class GetDownloadSize(BaseOperation):
    """
    A class to retrieve the download size of the dataset.

    Methods
    -------
    execute()
        Retrieves the download size of the dataset.
    """

    def execute(self):
        """
        Retrieves the download size of the dataset.

        Returns
        -------
        int
            The download size of the dataset.
        """
        dataset_info = self.data_tonic.get_dataset_info()
        download_size = dataset_info.card_data.get('download_size', 0)
        self.log_info(f"Dataset download size: {download_size}")
        return download_size
