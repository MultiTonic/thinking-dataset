# @file thinking_dataset/utilities/command_utils.py
# @description Utility class for common command-related operations.
# @version 1.0.0
# @license MIT

import os
import pandas as pd
from ..utilities.log import Log
from dotenv import load_dotenv as dotenv


class CommandUtils:

    @staticmethod
    def load_dotenv():
        dotenv()
        vars = {
            "HF_READ_TOKEN": os.getenv("HF_READ_TOKEN"),
            "HF_WRITE_TOKEN": os.getenv("HF_WRITE_TOKEN"),
            "HF_ORG": os.getenv("HF_ORG"),
            "HF_USER": os.getenv("HF_USER"),
            "CONFIG_PATH": os.getenv("CONFIG_PATH", "config/config.yaml"),
        }
        return vars

    @staticmethod
    def print_dotenv(env_vars, log):
        Log.info("Environment Configuration:")
        for key, value in env_vars.items():
            Log.info(f"{key}: {value}")

    @staticmethod
    def verify_dotenv(dotenv, log):
        if not all(dotenv.values()):
            Log.error(
                log,
                "Environment validation failed. Some variables are not set.")
            return False
        Log.info("Environment variables validated successfully.")
        return True

    @staticmethod
    def read_data(file, type):
        if type == "parquet":
            return pd.read_parquet(file)
        elif type == "csv":
            return pd.read_csv(file)
        else:
            raise ValueError(f"Unsupported dataset type: {type}")

    @staticmethod
    def to(df, file, type):
        if type == "parquet":
            df.to_parquet(file, index=False)
        elif type == "csv":
            df.to_csv(file, index=False)
        else:
            raise ValueError(f"Unsupported dataset type: {type}")

    @staticmethod
    def camel_to_snake(name):
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
