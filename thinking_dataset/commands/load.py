"""
@file thinking_dataset/commands/load.py
@description CLI command to load downloaded dataset files into SQLite database.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import click
from dotenv import load_dotenv
from thinking_dataset.datasets.dataset import Dataset
from thinking_dataset.tonics.data_tonic import DataTonic
from thinking_dataset.utilities.log import Log


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
            os.getenv("HF_TOKEN")
        }
        Log.info(log, "Environment variables loaded successfully.")
        return env_vars
    except Exception as e:
        Log.error(log, f"Error loading environment variables: {e}")
        return None


def print_env_config(env_vars, log):
    try:
        Log.info(log, "Environment Configuration:")
        for key, value in env_vars.items():
            Log.info(log, f"{key}: {value}")
        Log.info("Environment configuration printed successfully.")
    except Exception as e:
        Log.error(log, f"Error printing environment configuration: {e}")


def construct_paths(root_dir, data_dir, log):
    try:
        base_dir = os.path.join(root_dir, data_dir)
        raw_dir = os.path.join(base_dir, "raw")
        processed_dir = os.path.join(base_dir, "processed")
        Log.info(
            log, f"Constructed paths: base_dir={base_dir}, "
            f"raw_dir={raw_dir}, processed_dir={processed_dir}")
        return raw_dir, processed_dir
    except Exception as e:
        Log.error(log, f"Error constructing paths: {e}")
        return None, None


def validate_env_variables(env_vars, log):
    try:
        if not all(env_vars.values()):
            Log.error(
                log,
                "Environment validation failed. Some variables are not set.")
            return False
        Log.info(log, "Environment variables validated successfully.")
        return True
    except Exception as e:
        Log.error(log, f"Error validating environment variables: {e}")
        return False


@click.command()
@click.option('--data-dir',
              default='data/raw',
              help='Directory containing raw dataset files.')
def load(data_dir):
    """
    Load downloaded dataset files into SQLite database.
    """
    log = Log.setup(__name__)
    Log.info(log, "Starting the load command.")

    env_vars = load_env_variables(log)
    if env_vars is None:
        Log.error(log, "Failed to load environment variables.")
        return

    print_env_config(env_vars, log)

    if not validate_env_variables(env_vars, log):
        Log.error(log, "Failed to validate environment variables.")
        return

    try:
        data_tonic = DataTonic(token=env_vars['HF_TOKEN'])
        Log.info(log, "Initialized DataTonic instance.")
    except Exception as e:
        Log.error(log, f"Error initializing DataTonic instance: {e}")
        return

    try:
        dataset = Dataset(config_path=env_vars['DATASET_CONFIG_PATH'],
                          db_config=env_vars['DATABASE_CONFIG_PATH'],
                          data_tonic=data_tonic)
        Log.info(log, "Initialized Dataset instance.")
    except Exception as e:
        Log.error(log, f"Error initializing Dataset instance: {e}")
        return

    if not dataset.load(data_dir, Log):
        Log.error(log, "Failed to load dataset files.")
    else:
        Log.info(
            log, f"Loaded all dataset files from {os.path.normpath(data_dir)}")


if __name__ == "__main__":
    load()
