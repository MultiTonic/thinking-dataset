"""
@file thinking_dataset/downloads/dataset_downloads.py
@description Provides functionalities related to dataset downloads.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
from thinking_dataset.datasets.base_dataset import BaseDataset

# Get the dataset type (e.g., 'parquet') from environment variables
HF_DATASET_TYPE = os.getenv("HF_DATASET_TYPE", 'parquet')


class DatasetDownloads(BaseDataset):
    """
    A class that extends BaseDataset to provide functionalities
    related to dataset downloads.

    Methods
    -------
    get_dataset_download_urls(dataset_id)
        Retrieves the download URLs for the dataset files with a specific type.
    get_dataset_permissions()
        Checks the permissions of the dataset.
    get_dataset_file_list()
        Retrieves a list of files in the dataset.
    """

    def get_dataset_download_urls(self, dataset_id):
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
        dataset_info = self.get_dataset_info(dataset_id)
        download_urls = [
            file.rfilename
            for file in dataset_info.siblings
            if file.rfilename.endswith(f'.{HF_DATASET_TYPE}')
        ]
        self.log_info(f"Dataset download URLs: {download_urls}")
        return download_urls

    def get_dataset_permissions(self):
        """
        Checks the permissions of the dataset.

        Returns
        -------
        bool
            True if the dataset is private, False otherwise.
        """
        dataset_info = self.get_dataset_info()
        self.log_info(f"Dataset permissions: {dataset_info.private}")
        return dataset_info.private

    def get_dataset_file_list(self):
        """
        Retrieves a list of files in the dataset.

        Returns
        -------
        list
            A list of files in the dataset.
        """
        dataset_info = self.get_dataset_info()
        file_list = dataset_info.siblings
        self.log_info(f"Dataset files: {file_list}")
        return file_list
