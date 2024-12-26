"""
@file thinking_dataset/dataset_info.py
@description Provides functionalities related to dataset information.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .base_dataset import BaseDataset


class DatasetInfo(BaseDataset):
    """
    A class that extends BaseDataset to provide functionalities
    related to dataset information.

    Methods
    -------
    get_dataset_download_size()
        Retrieves the download size of the dataset.
    get_dataset_configurations()
        Retrieves the configurations of the dataset.
    get_dataset_description()
        Retrieves the description of the dataset.
    get_dataset_license()
        Retrieves the license information of the dataset.
    get_dataset_split_information()
        Retrieves the split information of the dataset.
    """

    def get_dataset_download_size(self):
        """
        Retrieves the download size of the dataset.

        Returns
        -------
        int
            The download size of the dataset.
        """
        dataset_info = self.get_dataset_info()
        download_size = dataset_info.card_data.get('download_size', 0)
        self.log_info(f"Dataset download size: {download_size}")
        return download_size

    def get_dataset_configurations(self):
        """
        Retrieves the configurations of the dataset.

        Returns
        -------
        list
            A list of configurations for the dataset.
        """
        dataset_info = self.get_dataset_info()
        configs = dataset_info.card_data.get('configs', [])
        self.log_info(f"Dataset configurations: {configs}")
        return configs

    def get_dataset_description(self):
        """
        Retrieves the description of the dataset.

        Returns
        -------
        str
            The description of the dataset.
        """
        dataset_info = self.get_dataset_info()
        description = dataset_info.card_data.get('description', '')
        self.log_info(f"Dataset description: {description}")
        return description

    def get_dataset_license(self):
        """
        Retrieves the license information of the dataset.

        Returns
        -------
        str
            The license information of the dataset.
        """
        dataset_info = self.get_dataset_info()
        license_info = dataset_info.card_data.get('license', None)
        self.log_info(f"Dataset license: {license_info}")
        return license_info

    def get_dataset_split_information(self):
        """
        Retrieves the split information of the dataset.

        Returns
        -------
        list
            A list of splits in the dataset.
        """
        dataset_info = self.get_dataset_info()
        splits = dataset_info.card_data['dataset_info']['splits']
        self.log_info(f"Dataset splits: {splits}")
        return splits
