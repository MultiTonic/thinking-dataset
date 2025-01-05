# @file thinking_dataset/tonics/data_tonic.py
# @description Manages dataset operations and interacts with the HF API.
# @version 1.2.3
# @license MIT

import os
import logging
from huggingface_hub import HfApi
from thinking_dataset.utilities.log import Log
from thinking_dataset.datasets.operations import (
    GetDownloadUrls, GetDownloadFile, GetMetadata, GetInfo, GetCardContent,
    GetConfiguration, GetDescription, GetDownloadSize, GetFileList, GetLicense,
    GetPermissions, GetSplitInformation, GetTags, ListDatasets)


class DataTonic:
    """
    Manages dataset operations for a specified organization and dataset,
    and handles interactions with the HF API.
    """

    def __init__(self, read_token, write_token, org, user, config):
        try:
            self.log = Log.setup(self.__class__.__name__)
            self.read_token = read_token
            self.write_token = write_token
            self.org = org
            self.user = user
            self.config = config
            self.api = HfApi(token=read_token)
            self._initialize()
            Log.info(self.log, "DataTonic initialized successfully.")
        except Exception as e:
            Log.error(self.log,
                      f"Error initializing DataTonic: {e}",
                      exc_info=True)

    def _initialize(self):
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

    def _upload_file(self, file_path):
        try:
            logging.info(f"Uploading {file_path}")
            self.api.upload_file(file_path, self.org)
            logging.info(f"Successfully uploaded {file_path}")
        except Exception as e:
            logging.error(f"Failed to upload {file_path} with error: {e}")

    def push(self, processed_dir):
        include_files = self.config.include_files
        exclude_files = self.config.exclude_files

        for file_name in os.listdir(processed_dir):
            if file_name not in exclude_files and (not include_files or
                                                   file_name in include_files):
                self._upload_file(os.path.join(processed_dir, file_name))
