"""
@file thinking_dataset/datasets/operations/operation_types.py
@description Defines the OperationTypes enum for dataset operations.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from enum import Enum


class OperationTypes(Enum):
    GET_CONFIGURATION = "get_configuration"
    GET_DESCRIPTION = "get_description"
    GET_DOWNLOAD_SIZE = "get_download_size"
    GET_DOWNLOAD_URLS = "get_download_urls"
    GET_LICENSE = "get_license"
    GET_SPLIT_INFORMATION = "get_split_information"
    LIST_DATASETS = "list_datasets"
