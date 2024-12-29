"""
@file thinking_dataset/tonics/data_tonic.py
@description DataTonic class for managing dataset operations.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
import os
from thinking_dataset.connectors.connector \
    import Connector
from thinking_dataset.datasets.operations.get_download_urls \
    import GetDownloadUrls
from thinking_dataset.datasets.operations.get_download_file \
    import GetDownloadFile
from thinking_dataset.datasets.operations.get_metadata \
    import GetMetadata
from thinking_dataset.datasets.operations.get_info \
    import GetInfo
from thinking_dataset.datasets.operations.get_card_content \
    import GetCardContent
from thinking_dataset.datasets.operations.get_configuration \
    import GetConfiguration
from thinking_dataset.datasets.operations.get_description \
    import GetDescription
from thinking_dataset.datasets.operations.get_download_size \
    import GetDownloadSize
from thinking_dataset.datasets.operations.get_file_list \
    import GetFileList
from thinking_dataset.datasets.operations.get_license \
    import GetLicense
from thinking_dataset.datasets.operations.get_permissions \
    import GetPermissions
from thinking_dataset.datasets.operations.get_split_information \
    import GetSplitInformation
from thinking_dataset.datasets.operations.get_tags \
    import GetTags
from thinking_dataset.datasets.operations.list_datasets \
    import ListDatasets

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
    get_info : GetInfo
        An instance of the GetInfo class for retrieving dataset information.
    get_card_content : GetCardContent
        An instance of the GetCardContent class for retrieving card content.
    get_configuration : GetConfiguration
        An instance of the GetConfiguration class for retrieving configuration.
    get_description : GetDescription
        An instance of the GetDescription class for retrieving description.
    get_download_size : GetDownloadSize
        An instance of the GetDownloadSize class for retrieving download size.
    get_file_list : GetFileList
        An instance of the GetFileList class for retrieving file list.
    get_license : GetLicense
        An instance of the GetLicense class for retrieving license information.
    get_permissions : GetPermissions
        An instance of the GetPermissions class for retrieving permissions.
    get_split_information : GetSplitInformation
        An instance of the GetSplitInformation class for split information.
    get_tags : GetTags
        An instance of the GetTags class for retrieving tags.
    list_datasets : ListDatasets
        An instance of the ListDatasets class for listing datasets.

    Methods
    -------
    None
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
        self.get_info = GetInfo(self)
        self.get_card_content = GetCardContent(self)
        self.get_configuration = GetConfiguration(self)
        self.get_description = GetDescription(self)
        self.get_download_size = GetDownloadSize(self)
        self.get_file_list = GetFileList(self)
        self.get_license = GetLicense(self)
        self.get_permissions = GetPermissions(self)
        self.get_split_information = GetSplitInformation(self)
        self.get_tags = GetTags(self)
        self.list_datasets = ListDatasets(self)
