"""
@file thinking_dataset/datasets/operations/get_download_size.py
@description Retrieves the download size of the dataset.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .base_operation import BaseOperation
from ...utilities.log import Log


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
        Log.info(self.log, f"Dataset download size: {download_size}")
        return download_size
