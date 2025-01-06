# @file thinking_dataset/datasets/operations/operation_types.py
# @description Defines the OperationTypes enum for dataset operations.
# @version 1.0.0
# @license MIT

from enum import Enum


class OperationTypes(Enum):
    GET_CARD_CONTENT = "get_card_content"
    GET_CONFIGURATION = "get_configuration"
    GET_DESCRIPTION = "get_description"
    GET_DOWNLOAD_SIZE = "get_download_size"
    GET_DOWNLOAD_URLS = "get_download_urls"
    GET_FILE_LIST = "get_file_list"
    GET_INFO = "get_info"
    GET_LICENSE = "get_license"
    GET_METADATA = "get_metadata"
    GET_PERMISSIONS = "get_permissions"
    GET_SPLIT_INFORMATION = "get_split_information"
    GET_TAGS = "get_tags"
    GET_WHOAMI = "get_whoami"
    LIST_DATASETS = "list_datasets"
