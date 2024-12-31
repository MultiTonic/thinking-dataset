"""
@file thinking_dataset/utilities/command_utils.py
@description Utility class for common command-related operations.
@version 1.0.0
@license MIT
"""

import os
from dotenv import load_dotenv
from thinking_dataset.utilities.log import Log as Log


class CommandUtils:

    @staticmethod
    def load_env_variables(log):
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
    def print_env_config(env_vars, log):
        Log.info(log, "Environment Configuration:")
        for key, value in env_vars.items():
            Log.info(log, f"{key}: {value}")
        Log.info(log, "Environment configuration printed successfully.")

    @staticmethod
    def construct_paths(root_dir, data_dir, log):
        base_dir = os.path.join(root_dir, data_dir)
        raw_dir = os.path.join(base_dir, "raw")
        Log.info(log,
                 f"Constructed paths: base_dir={base_dir}, raw_dir={raw_dir}")
        return raw_dir

    @staticmethod
    def validate_env_variables(env_vars, log):
        if not all(env_vars.values()):
            Log.error(
                log,
                "Environment validation failed. Some variables are not set.")
            return False
        Log.info(log, "Environment variables validated successfully.")
        return True
