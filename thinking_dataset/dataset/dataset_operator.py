# @file thinking_dataset/dataset/dataset_operator.py
# @description Implementation of the DatasetOperator class.
# @version 1.0.5
# @license MIT

from typing import List, Optional
from thinking_dataset.utils.log import Log
from thinking_dataset.dataset.operations import (
    DownloadOperation, GetCardContent, GetConfiguration, GetDescription,
    GetDownloadFile, GetDownloadSize, GetDownloadUrls, GetFileList, GetInfo,
    GetLicense, GetMetadata, GetPermissions, GetSplitInformation, GetTags,
    GetWhoami, ListDatasets, LoadOperation, OperationTypes)

OT = OperationTypes


class DatasetOperator:
    """
    A class to bind all dataset operations into a usable kernel.
    """

    def __init__(self, api, attributes, database):
        self.api = api
        self.attributes = attributes
        self.database = database
        self.ops = {
            OT.GET_DOWNLOAD_FILE: GetDownloadFile(self.api),
            OT.GET_DOWNLOAD_URLS: GetDownloadUrls(self.api),
            OT.LIST_DATASETS: ListDatasets(self.api),
            OT.DOWNLOAD: DownloadOperation(self.api, self.attributes),
            OT.LOAD: LoadOperation(self.database),
            OT.GET_CARD_CONTENT: GetCardContent(self.api),
            OT.GET_CONFIGURATION: GetConfiguration(self.api),
            OT.GET_DESCRIPTION: GetDescription(self.api),
            OT.GET_DOWNLOAD_SIZE: GetDownloadSize(self.api),
            OT.GET_FILE_LIST: GetFileList(self.api),
            OT.GET_INFO: GetInfo(self.api),
            OT.GET_LICENSE: GetLicense(self.api),
            OT.GET_METADATA: GetMetadata(self.api),
            OT.GET_PERMISSIONS: GetPermissions(self.api),
            OT.GET_SPLIT_INFORMATION: GetSplitInformation(self.api),
            OT.GET_TAGS: GetTags(self.api),
            OT.GET_WHOAMI: GetWhoami(self.api),
        }

        Log.info("DatasetOperator initialized successfully!")

    def download(self) -> bool:
        return self.ops[OT.DOWNLOAD].execute()

    def download_file(self, repo_id: str, filename: str, local_dir: str,
                      token: str):
        return self.ops[OT.GET_DOWNLOAD_FILE].execute(repo_id, filename,
                                                      local_dir, token)

    def get_card_content(self, *args, **kwargs):
        return self.ops[OT.GET_CARD_CONTENT].execute(*args, **kwargs)

    def get_configuration(self, *args, **kwargs):
        return self.ops[OT.GET_CONFIGURATION].execute(*args, **kwargs)

    def get_description(self, *args, **kwargs):
        return self.ops[OT.GET_DESCRIPTION].execute(*args, **kwargs)

    def get_download_size(self, *args, **kwargs):
        return self.ops[OT.GET_DOWNLOAD_SIZE].execute(*args, **kwargs)

    def get_download_urls(self, dataset_id: str):
        return self.ops[OT.GET_DOWNLOAD_URLS].execute(dataset_id)

    def get_file_list(self, *args, **kwargs):
        return self.ops[OT.GET_FILE_LIST].execute(*args, **kwargs)

    def get_info(self, *args, **kwargs):
        return self.ops[OT.GET_INFO].execute(*args, **kwargs)

    def get_license(self, *args, **kwargs):
        return self.ops[OT.GET_LICENSE].execute(*args, **kwargs)

    def get_metadata(self, *args, **kwargs):
        return self.ops[OT.GET_METADATA].execute(*args, **kwargs)

    def get_permissions(self, *args, **kwargs):
        return self.ops[OT.GET_PERMISSIONS].execute(*args, **kwargs)

    def get_split_information(self, *args, **kwargs):
        return self.ops[OT.GET_SPLIT_INFORMATION].execute(*args, **kwargs)

    def get_tags(self, *args, **kwargs):
        return self.ops[OT.GET_TAGS].execute(*args, **kwargs)

    def get_whoami(self, *args, **kwargs):
        return self.ops[OT.GET_WHOAMI].execute(*args, **kwargs)

    def list_datasets(self):
        return self.ops[OT.LIST_DATASETS].execute()

    def load(self, files_to_load: Optional[List[str]] = None) -> bool:
        return self.ops[OT.LOAD].execute(files_to_load)
