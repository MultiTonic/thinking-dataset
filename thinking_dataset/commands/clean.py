"""
@file thinking_dataset/commands/clean.py
@description Command to clean the data directory and other dynamic resources.
@version 1.0.0
@license MIT
"""

import os
import shutil
import click
from ..utilities.log import Log
from ..config.dataset_config import DatasetConfig


@click.command()
def clean():
    """
    Cleans the data directory and other dynamic resources.
    """
    log = Log.setup(__name__)
    Log.info(log, "Starting the clean command.")

    try:
        # Load dataset configuration
        dataset_config = DatasetConfig(
            os.getenv('DATASET_CONFIG_PATH', 'config/dataset_config.yaml'))
        dataset_config.validate()

        base_dir_path = os.path.abspath(
            os.path.join(os.path.expanduser(dataset_config.ROOT_DIR),
                         dataset_config.DATA_DIR))

        if os.path.exists(base_dir_path):
            shutil.rmtree(base_dir_path)
            Log.info(log, f"Removed directory: {base_dir_path}")
        else:
            Log.info(log, f"No directory found at {base_dir_path}")

        os.makedirs(base_dir_path)
        Log.info(log, f"Created clean directory: {base_dir_path}")

    except PermissionError as e:
        Log.error(log, f"PermissionError: {e}", exc_info=True)
    except Exception as e:
        Log.error(log, f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    clean()
