"""
@file thinking_dataset/tonics/data_tonic.py
@description DataTonic class for managing dataset operations.
@version 1.0.0
@license MIT
@param Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
import os
from huggingface_hub.utils import RepositoryNotFoundError
from thinking_dataset.connectors.connector import Connector
from thinking_dataset.datasets.operations.get_download_urls import (
    GetDownloadUrls, )
from thinking_dataset.datasets.operations.get_download_file import (
    GetDownloadFile, )
from thinking_dataset.datasets.operations.get_metadata import GetMetadata

HF_ORGANIZATION = os.getenv("HF_ORGANIZATION")
HF_DATASET = os.getenv("HF_DATASET")


class DataTonic(Connector):
    """
    A class that extends Connector to manage dataset operations for a
    specified organization and dataset.

    Attributes
    ----------
    organization : str
        The organization to which the datasets belong.
    dataset : str
        The specific dataset to manage.
    HF_DATASET_TYPE : str
        The dataset type (e.g., 'parquet') for file extensions.
    get_download_urls : GetDownloadUrls
        An instance of the GetDownloadUrls class for retrieving download URLs.
    get_download_file : GetDownloadFile
        An instance of the GetDownloadFile class for downloading files.
    get_metadata : GetMetadata
        An instance of the GetMetadata class for retrieving dataset metadata.

    Methods
    -------
    get_dataset_info(dataset_id)
        Retrieves dataset information for the given dataset ID.
    """

    def __init__(self,
                 token,
                 organization=HF_ORGANIZATION,
                 dataset=HF_DATASET):
        """
        Constructs all the necessary attributes for the DataTonic object.

        Parameters
        ----------
        token : str
            The API token for authentication.
        organization : str, optional
            The organization to which the datasets belong
            (default is HF_ORGANIZATION).
        dataset : str, optional
            The specific dataset to manage (default is HF_DATASET).
        """
        super().__init__(token)
        self.organization = organization
        self.dataset = dataset
        self.HF_DATASET_TYPE = os.getenv("HF_DATASET_TYPE", "parquet")
        self.get_download_urls = GetDownloadUrls(self)
        self.get_download_file = GetDownloadFile(self)
        self.get_metadata = GetMetadata(self)

    def get_dataset_info(self, dataset_id):
        try:
            return self.api.dataset_info(dataset_id)
        except RepositoryNotFoundError as e:
            print(f"Error retrieving dataset info for {dataset_id}: {e}")
            raise
