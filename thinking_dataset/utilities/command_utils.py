"""
@file thinking_dataset/utilities/command_utils.py
@description Utility class for common command-related operations.
@version 1.0.0
@license MIT
"""

import os
import importlib
from dotenv import load_dotenv
from thinking_dataset.utilities.log import Log as Log
import pandas as pd


class CommandUtils:

    @staticmethod
    def load_env_vars(log):
        load_dotenv()
        env_vars = {
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
        Log.info(log, "Environment variables loaded successfully.")
        return env_vars

    @staticmethod
    def print_env_vars(env_vars, log):
        Log.info(log, "Environment Configuration:")
        for key, value in env_vars.items():
            Log.info(log, f"{key}: {value}")
        Log.info(log, "Environment configuration printed successfully.")

    @staticmethod
    def validate_env_vars(env_vars, log):
        if not all(env_vars.values()):
            Log.error(
                log,
                "Environment validation failed. Some variables are not set.")
            return False
        Log.info(log, "Environment variables validated successfully.")
        return True

    @staticmethod
    def load_dataset_config(dataset_config_path):
        """
        Load and validate the dataset configuration.
        """
        from ..config.dataset_config import DatasetConfig
        dataset_config = DatasetConfig(dataset_config_path)
        dataset_config.validate()
        return dataset_config

    @staticmethod
    def read_data(input_file, dataset_type):
        """
        Load data from the specified file based on the dataset type.
        """
        if dataset_type == "parquet":
            return pd.read_parquet(input_file)
        elif dataset_type == "csv":
            return pd.read_csv(input_file)
        else:
            raise ValueError(f"Unsupported dataset type: {dataset_type}")

    @staticmethod
    def save_data(df, output_file, dataset_type):
        """
        Save data to the specified file based on the dataset type.
        """
        if dataset_type == "parquet":
            df.to_parquet(output_file, index=False)
        elif dataset_type == "csv":
            df.to_csv(output_file, index=False)
        else:
            raise ValueError(f"Unsupported dataset type: {dataset_type}")

    @staticmethod
    def camel_to_snake(name):
        """
        Convert CamelCase to snake_case.
        """
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def get_pipe_class(pipe_type, log):
        """
        Dynamically import and return the pipe class based on the pipe type.
        """
        module_name = "thinking_dataset.pipeworks.pipes." + \
            CommandUtils.camel_to_snake(pipe_type)

        try:
            module = importlib.import_module(module_name)
            return getattr(module, pipe_type)
        except (ImportError, AttributeError) as e:
            Log.error(
                log, f"Error loading pipe class {pipe_type} "
                f"from module {module_name}: {e}")
            raise
