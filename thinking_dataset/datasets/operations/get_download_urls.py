"""
@file thinking_dataset/datasets/operations/get_download_urls.py
@description Operation to retrieve dataset download URLs.
@version 1.0.0
@license MIT
"""

from .base_operation import Operation
from ...utilities.log import Log


class GetDownloadUrls(Operation):
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
            if file.rfilename.endswith(f'.{self.config.dataset_type}')
        ]
        Log.info(f"Dataset download URLs: {download_urls}")
        return download_urls
