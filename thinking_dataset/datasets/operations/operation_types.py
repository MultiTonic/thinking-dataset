"""
@file thinking_dataset/datasets/operations/operation_types.py
@description Defines the OperationTypes enum for dataset operations.
@version 1.0.0
@license MIT
@author Kara Rawson
@see https://github.com/MultiTonic/thinking-dataset
@see https://huggingface.co/DataTonic
"""

from enum import Enum


class OperationTypes(Enum):
    LIST_ORGANIZATION_DATASETS = "list_organization_datasets"
    GET_DATASET_METADATA = "get_dataset_metadata"
    GET_DATASET_TAGS = "get_dataset_tags"
    GET_DATASET_CARD_CONTENT = "get_dataset_card_content"
