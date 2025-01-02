"""
@file thinking_dataset/utilities/command_utils.py
@description Utility class for common command-related operations.
@version 1.0.0
@license MIT
"""

import os
import pandas as pd
from ..utilities.log import Log
from dotenv import load_dotenv as dotenv


class CommandUtils:

    @staticmethod
    def load_dotenv():
        dotenv()
        vars = {
            "ROOT_DIR":
            os.path.abspath(os.getenv("ROOT_DIR", ".")),
            "DATA_DIR":
            os.getenv("DATA_DIR", "data"),
            "DATABASE_CONFIG_PATH":
            os.getenv("DATABASE_CONFIG_PATH", "config/database_config.yaml"),
            "DATASET_CONFIG_PATH":
            os.getenv("DATASET_CONFIG_PATH", "config/dataset_config.yaml"),
            "HF_TOKEN":
            os.getenv("HF_TOKEN"),
            "HF_ORGANIZATION":
            os.getenv("HF_ORGANIZATION"),
            "HF_DATASET":
            os.getenv("HF_DATASET"),
        }
        return vars

    @staticmethod
    def print_dotenv(env_vars, log):
        Log.info(log, "Environment Configuration:")
        for key, value in env_vars.items():
            Log.info(log, f"{key}: {value}")

    @staticmethod
    def verify_dotenv(dotenv, log):
        if not all(dotenv.values()):
            Log.error(
                log,
                "Environment validation failed. Some variables are not set.")
            return False
        Log.info(log, "Environment variables validated successfully.")
        return True

    @staticmethod
    def load_dataset_config(config_path):
        """
        Load and validate the dataset configuration.
        """
        from ..config.dataset_config import DatasetConfig
        config = DatasetConfig(config_path)
        config.validate()
        return config

    @staticmethod
    def read_data(file, type):
        """
        Load data from the specified file based on the dataset type.
        """
        if type == "parquet":
            return pd.read_parquet(file)
        elif type == "csv":
            return pd.read_csv(file)
        else:
            raise ValueError(f"Unsupported dataset type: {type}")

    @staticmethod
    def to(df, file, type):
        """
        Save data to the specified file based on the dataset type.
        """
        if type == "parquet":
            df.to_parquet(file, index=False)
        elif type == "csv":
            df.to_csv(file, index=False)
        else:
            raise ValueError(f"Unsupported dataset type: {type}")

    @staticmethod
    def camel_to_snake(name):
        """
        Convert CamelCase to snake_case.
        """
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
