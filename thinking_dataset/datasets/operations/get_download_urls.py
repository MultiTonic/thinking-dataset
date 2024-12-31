"""
@file thinking_dataset/datasets/operations/get_download_urls.py
@description Operation to retrieve dataset download URLs.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|GitHub Organization}
"""

from .base_operation import BaseOperation
from ...utilities.log import Log


class GetDownloadUrls(BaseOperation):
    """
    Operation class to retrieve dataset download URLs.
    """

    def execute(self, dataset_id):
        """
        Retrieves the download URLs for the dataset files with a specific type.
        """
        dataset_info = self.data_tonic.get_info.execute(dataset_id)
        download_urls = [
            file.rfilename for file in dataset_info.siblings
            if file.rfilename.endswith(f'.{self.config.DATASET_TYPE}')
        ]
        Log.info(self.log, f"Dataset download URLs: {download_urls}")
        return download_urls
