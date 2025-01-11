# @file thinking_dataset/tonics/data_tonic.py
# @description Manages dataset operations and interacts with the Hf Api.
# @version 1.2.13
# @license MIT

import thinking_dataset.config as conf
import thinking_dataset.dataset.dataset_attributes as Attr

from huggingface_hub import HfApi
from thinking_dataset.utils.log import Log

from thinking_dataset.dataset.operations import (
    DownloadOperation, GetDownloadUrls, GetDownloadFile, GetMetadata, GetInfo,
    GetCardContent, GetConfiguration, GetDescription, GetDownloadSize,
    GetFileList, GetLicense, GetPermissions, GetSplitInformation, GetTags,
    GetWhoami, ListDatasets, LoadOperation)

CK = conf.config_keys.ConfigKeys


class DataTonic:
    """
    Manages dataset operations for a specified organization and dataset,
    and handles interactions with the Hf Api and DataTonic.
    """

    def __init__(self, read_token, write_token, org, user):
        try:
            self.read_token = read_token
            self.write_token = write_token
            self.organization = org
            self.user = user
            self.dataset = conf.get_value(CK.DATASET_NAME)
            self.dataset_type = conf.get_value(CK.DATABASE_TYPE)
            self.api = HfApi(token=read_token)
            self.attributes = Attr.DatasetAttributes().attributes
            self.download_operation = DownloadOperation(
                self.api, self.attributes)
            self.get_card_content = GetCardContent(self)
            self.get_configuration = GetConfiguration(self)
            self.get_description = GetDescription(self)
            self.get_download_file = GetDownloadFile(self)
            self.get_download_size = GetDownloadSize(self)
            self.get_download_urls = GetDownloadUrls(self)
            self.get_file_list = GetFileList(self)
            self.get_info = GetInfo(self)
            self.get_license = GetLicense(self)
            self.get_metadata = GetMetadata(self)
            self.get_permissions = GetPermissions(self)
            self.get_split_information = GetSplitInformation(self)
            self.get_tags = GetTags(self)
            self.get_whoami = GetWhoami(self)
            self.list_datasets = ListDatasets(self)
            self.load_operation = LoadOperation(self)
            Log.info("DataTonic initialized successfully!")
        except Exception as e:
            Log.error(f"Error initializing DataTonic: {e}", exc_info=True)
            raise e
