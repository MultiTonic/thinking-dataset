# @file thinking_dataset/config/config_keys.py
# @description Defines keys used in the dataset configuration.
# @version 1.0.1
# @license MIT

from enum import Enum


class ConfigKeys(Enum):
    DATASET_NAME = "dataset_name"
    DATASET_TYPE = "dataset_type"
    DATABASE_URL = "database_url"
    DATABASE_TYPE = "database_type"
    POOL_SIZE = "pool_size"
    MAX_OVERFLOW = "max_overflow"
    CONNECT_TIMEOUT = "connect_timeout"
    READ_TIMEOUT = "read_timeout"
    LOG_QUERIES = "log_queries"
    ENVIRONMENT = "environment"
    DATABASE_NAME = "database_name"
    ROOT_PATH = "root"
    TEMPLATES_PATH = "templates"
    DATA_PATH = "data"
    RAW_PATH = "raw"
    PROCESS_PATH = "process"
    EXPORT_PATH = "export"
    GENERATE_PATH = "generate"
    DATABASE_PATH = "database"
    PROCESSED_DATA_PATH = "processed_data"
    PROCESSED_DATA_TRAIN_PATH = "processed_data/train"
    INCLUDE_FILES = "include_files"
    EXCLUDE_FILES = "exclude_files"
    LOAD_PATTERNS = "load_patterns"
    PIPELINES = "pipelines"
    HF_READ_TOKEN = "HF_READ_TOKEN"
    HF_WRITE_TOKEN = "HF_WRITE_TOKEN"
    HF_ORG = "HF_ORG"
    HF_USER = "HF_USER"
    CONFIG_PATH = "CONFIG_PATH"
