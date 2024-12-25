"""
@file thinking_dataset/data_tonic.py
@description DataTonic class for managing dataset operations.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
from .connector import Connector
from .dataset_operations import DatasetOperations
from .dataset_downloads import DatasetDownloads
from .dataset_info import DatasetInfo

HF_ORGANIZATION = os.getenv("HF_ORGANIZATION")
HF_DATASET = os.getenv("HF_DATASET")


class DataTonic(Connector):
    """
    A class that extends Connector to manage dataset operations for
    a specified organization and dataset.

    Attributes
    ----------
    organization : str
        The organization to which the datasets belong.
    dataset : str
        The specific dataset to manage.
    operations : DatasetOperations
        An instance of the DatasetOperations class for dataset operations.
    downloads : DatasetDownloads
        An instance of the DatasetDownloads class for dataset downloads.
    info : DatasetInfo
        An instance of the DatasetInfo class for dataset information.

    Methods
    -------
    N/A
    """

    def __init__(
        self,
        token,
        organization=HF_ORGANIZATION,
        dataset=HF_DATASET
    ):
        """
        Constructs all the necessary attributes for the DataTonic object.

        Parameters
        ----------
        token : str
            The API token for authentication.
        organization : str, optional
            The org of datasets belong (default is HF_ORGANIZATION).
        dataset : str, optional
            The specific dataset to manage (default is HF_DATASET).
        """
        super().__init__(token)
        self.organization = organization
        self.dataset = dataset
        self.operations = DatasetOperations(self)
        self.downloads = DatasetDownloads(self)
        self.info = DatasetInfo(self)
