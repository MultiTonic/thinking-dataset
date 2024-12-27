"""
@file thinking_dataset/datasets/operations/get_download_urls.py
@description Operation to retrieve dataset download URLs.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .base_operation import BaseOperation


class GetDownloadUrls(BaseOperation):
    """
    Operation class to retrieve dataset download URLs.
    """

    def execute(self, dataset_id):
        """
        Retrieves the download URLs for the dataset files with a specific type.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to retrieve download URLs for.

        Returns
        -------
        list
            A list of download URLs for the dataset files.
        """
        dataset_info = self.data_tonic.get_dataset_info(dataset_id)
        download_urls = [
            file.rfilename for file in dataset_info.siblings
            if file.rfilename.endswith(f'.{self.data_tonic.HF_DATASET_TYPE}')
        ]
        self.log_info(f"Dataset download URLs: {download_urls}")
        return download_urls
