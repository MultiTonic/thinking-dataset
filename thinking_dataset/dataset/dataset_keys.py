# @file thinking_dataset/datasets/dataset_keys.py
# @description Contains key names for dataset attributes.
# @version 1.0.1
# @license MIT

from enum import Enum


class DatasetKeys(Enum):
    ORG = "org"
    NAME = "name"
    TYPE = "type"
    INCLUDE = "include"
    EXCLUDE = "exclude"
    DATABASE = "database"
    READ_TOKEN = "read_token"
    WRITE_TOKEN = "write_token"
