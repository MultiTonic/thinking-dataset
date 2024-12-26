"""
@file thinking_dataset/dataset_operations.py
@description Provides functionalities related to dataset operations.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from ..datasets.base_dataset import BaseDataset


class DatasetOperations(BaseDataset):
    """
    A class that extends BaseDataset to provide functionalities
    related to dataset operations.

    Methods
    -------
    list_organization_datasets()
        Lists datasets associated with the organization.
    get_dataset_metadata()
        Retrieves metadata about the dataset.
    get_dataset_tags()
        Retrieves tags associated with the dataset.
    get_dataset_card_content()
        Retrieves card content of the dataset.
    """

    def list_organization_datasets(self):
        """
        Lists datasets associated with the organization.

        Returns
        -------
        list
            A list of datasets associated with the organization.
        """
        datasets = self.data_tonic.list_datasets(
            author=self.data_tonic.organization)
        self.log_info(
            f"Number of {self.data_tonic.organization} datasets listed: "
            f"{len(datasets)}")

        return datasets

    def get_dataset_metadata(self):
        """
        Retrieves metadata about the dataset.

        Returns
        -------
        DatasetInfo
            Metadata about the specified dataset.
        """
        dataset_info = self.get_dataset_info()
        self.log_info(f"Dataset metadata: {dataset_info}")
        return dataset_info

    def get_dataset_tags(self):
        """
        Retrieves tags associated with the dataset.

        Returns
        -------
        list
            A list of tags associated with the dataset.
        """
        dataset_info = self.get_dataset_info()
        self.log_info(f"Dataset tags: {dataset_info.tags}")
        return dataset_info.tags

    def get_dataset_card_content(self):
        """
        Retrieves card content of the dataset.

        Returns
        -------
        dict
            The card content of the dataset.
        """
        dataset_info = self.get_dataset_info()
        self.log_info(f"Dataset card data: {dataset_info.card_data}")
        return dataset_info.card_data
