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
from thinking_dataset.utilities.log import Log
from thinking_dataset.connectors.connector import Connector
from thinking_dataset.datasets.operations.get_download_urls \
    import GetDownloadUrls
from thinking_dataset.datasets.operations.get_download_file \
    import GetDownloadFile
from thinking_dataset.datasets.operations.get_metadata import GetMetadata
from thinking_dataset.datasets.operations.get_info import GetInfo
from thinking_dataset.datasets.operations.get_card_content \
    import GetCardContent
from thinking_dataset.datasets.operations.get_configuration \
    import GetConfiguration
from thinking_dataset.datasets.operations.get_description import GetDescription
from thinking_dataset.datasets.operations.get_download_size \
    import GetDownloadSize
from thinking_dataset.datasets.operations.get_file_list import GetFileList
from thinking_dataset.datasets.operations.get_license import GetLicense
from thinking_dataset.datasets.operations.get_permissions import GetPermissions
from thinking_dataset.datasets.operations.get_split_information \
    import GetSplitInformation
from thinking_dataset.datasets.operations.get_tags import GetTags
from thinking_dataset.datasets.operations.list_datasets import ListDatasets


class DataTonic(Connector):
    """
    A class that extends Connector to manage dataset operations for a
    specified organization and dataset.
    """

    def __init__(self, token, organization, dataset, config):
        """
        Constructs all the necessary attributes for the DataTonic object.
        """
        try:
            super().__init__(token)
            self.log = Log.setup(self.__class__.__name__)
            self.organization = organization
            self.dataset = dataset
            self.config = config
            self.HF_DATASET_TYPE = os.getenv("HF_DATASET_TYPE", "parquet")
            self._initialize_operations()
            Log.info(self.log, "DataTonic initialized successfully.")
        except Exception as e:
            Log.error(self.log,
                      f"Error initializing DataTonic: {e}",
                      exc_info=True)

    def _initialize_operations(self):
        self.get_download_urls = GetDownloadUrls(self, self.config)
        self.get_download_file = GetDownloadFile(self, self.config)
        self.get_metadata = GetMetadata(self, self.config)
        self.get_info = GetInfo(self, self.config)
        self.get_card_content = GetCardContent(self, self.config)
        self.get_configuration = GetConfiguration(self, self.config)
        self.get_description = GetDescription(self, self.config)
        self.get_download_size = GetDownloadSize(self, self.config)
        self.get_file_list = GetFileList(self, self.config)
        self.get_license = GetLicense(self, self.config)
        self.get_permissions = GetPermissions(self, self.config)
        self.get_split_information = GetSplitInformation(self, self.config)
        self.get_tags = GetTags(self, self.config)
        self.list_datasets = ListDatasets(self, self.config)
        Log.info(self.log, "Operations initialized successfully.")
