# @file thinking_dataset/tonics/data_tonic.py
# @description Manages dataset operations and interacts with the HF API.
# @version 1.2.3
# @license MIT

from huggingface_hub import HfApi
from thinking_dataset.utils.log import Log
from thinking_dataset.datasets.operations import (
    GetDownloadUrls, GetDownloadFile, GetMetadata, GetInfo, GetCardContent,
    GetConfiguration, GetDescription, GetDownloadSize, GetFileList, GetLicense,
    GetPermissions, GetSplitInformation, GetTags, ListDatasets)


class DataTonic:
    """
    Manages dataset operations for a specified organization and dataset,
    and handles interactions with the HF API.
    """

    def __init__(self, read_token, write_token, org, user):
        try:
            self.read_token = read_token
            self.write_token = write_token
            self.org = org
            self.user = user
            self.api = HfApi(token=read_token)
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
            Log.info("DataTonic initialized successfully.")
        except Exception as e:
            Log.error(f"Error initializing DataTonic: {e}", exc_info=True)
            raise e
