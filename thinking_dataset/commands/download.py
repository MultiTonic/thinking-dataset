"""
@file thinking_dataset/commands/download.py
@description CLI command to download datasets from Hugging Face.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import sys
import click
from dotenv import load_dotenv
from thinking_dataset.datasets.dataset import Dataset
from thinking_dataset.tonics.data_tonic import DataTonic
from thinking_dataset.utilities.log import Log as Log
from thinking_dataset.config.dataset_config import DatasetConfig


def load_env_variables(log):
    try:
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
    except Exception as e:
        Log.error(log,
                  f"Error loading environment variables: {e}",
                  exc_info=True)
        sys.exit(1)


def print_env_config(env_vars, log):
    try:
        Log.info(log, "Environment Configuration:")
        for key, value in env_vars.items():
            Log.info(log, f"{key}: {value}")
        Log.info(log, "Environment configuration printed successfully.")
    except Exception as e:
        Log.error(log,
                  f"Error printing environment configuration: {e}",
                  exc_info=True)
        sys.exit(1)


def construct_paths(root_dir, data_dir, logger):
    try:
        base_dir = os.path.join(root_dir, data_dir)
        raw_dir = os.path.join(base_dir, "raw")
        processed_dir = os.path.join(base_dir, "processed")
        Log.info(
            Log, f"Constructed paths: base_dir={base_dir}, "
            f"raw_dir={raw_dir}, processed_dir={processed_dir}")
        return raw_dir, processed_dir
    except Exception as e:
        Log.error(logger, f"Error constructing paths: {e}", exc_info=True)
        sys.exit(1)


def validate_env_variables(env_vars, logger):
    try:
        if not all(env_vars.values()):
            Log.error(
                logger,
                "Environment validation failed. Some variables are not set.")
            return False
        Log.info(logger, "Environment variables validated successfully.")
        return True
    except Exception as e:
        Log.error(logger,
                  f"Error validating environment variables: {e}",
                  exc_info=True)
        return False


@click.command()
@click.option('--data-dir',
              default='data/raw',
              help='Directory containing raw dataset files.')
def download(data_dir):
    """
    Download datasets from Hugging Face.
    """
    log = Log.setup(__name__)
    Log.info(log, "Starting the download command.")

    env_vars = load_env_variables(log)
    if env_vars is None:
        Log.error(log, "Failed to load environment variables.")
        sys.exit(1)

    print_env_config(env_vars, log)

    if not validate_env_variables(env_vars, log):
        Log.error(log, "Failed to validate environment variables.")
        sys.exit(1)

    try:
        dataset_config_path = env_vars['DATASET_CONFIG_PATH']
        dataset_config = DatasetConfig(dataset_config_path)
        dataset_config.validate()

        data_tonic = DataTonic(token=env_vars['HF_TOKEN'],
                               organization=env_vars['HF_ORGANIZATION'],
                               dataset=env_vars['HF_DATASET'],
                               config=dataset_config)
        Log.info(log, "Initialized DataTonic instance.")
    except Exception as e:
        Log.error(log,
                  f"Error initializing DataTonic instance: {e}",
                  exc_info=True)
        sys.exit(1)

    try:
        dataset = Dataset(data_tonic=data_tonic)
        Log.info(log, "Initialized Dataset instance.")
    except Exception as e:
        Log.error(log,
                  f"Error initializing Dataset instance: {e}",
                  exc_info=True)
        sys.exit(1)

    if not dataset.download(
            env_vars['HF_TOKEN'],
            f"{env_vars['HF_ORGANIZATION']}/{env_vars['HF_DATASET']}"):
        Log.error(log, "Failed to download dataset files.")
        sys.exit(1)
    else:
        Log.info(
            log,
            f"Downloaded all dataset files to {os.path.normpath(data_dir)}")


if __name__ == "__main__":
    download()
