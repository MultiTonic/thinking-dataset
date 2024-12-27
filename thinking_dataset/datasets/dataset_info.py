"""
@file thinking_dataset/dataset_info.py
@description Provides functionalities related to dataset information.
@version 1.0.0
@license MIT
author Kara Rawson
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
    get_description()
        Retrieves the description of the dataset.
    get_license()
        Retrieves the license information of the dataset.
    get_split_information()
        Retrieves the split information of the dataset.
    """

    def get_description(self):
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

    def get_license(self):
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

    def get_split_information(self):
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
