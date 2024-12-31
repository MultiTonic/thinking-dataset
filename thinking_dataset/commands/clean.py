"""
@file thinking_dataset/commands/clean.py
@description Command to clean the data directory and other dynamic resources.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import shutil
import click
from dotenv import load_dotenv
from ..utilities.log import Log

# Load environment variables from .env file
load_dotenv()

ROOT_DIR = os.path.expanduser(os.getenv("ROOT_DIR", "."))
DATA_DIR = os.getenv("DATA_DIR", "data")


def clean_data_directory(log):
    """
    Cleans the data directory and other dynamic resources.
    """
    base_dir_path = os.path.abspath(os.path.join(ROOT_DIR, DATA_DIR))

    if os.path.exists(base_dir_path):
        try:
            shutil.rmtree(base_dir_path)
            Log.info(log, f"Removed directory: {base_dir_path}")
        except PermissionError as e:
            Log.error(log, f"PermissionError: {e}", exc_info=True)
    else:
        Log.info(log, f"No directory found at {base_dir_path}")

    try:
        os.makedirs(base_dir_path)
        Log.info(log, f"Created clean directory: {base_dir_path}")
    except PermissionError as e:
        Log.error(log, f"PermissionError: {e}", exc_info=True)


@click.command()
def clean():
    """
    Cleans the data directory and other dynamic resources.
    """
    log = Log.setup(__name__)
    Log.info(log, "Starting the clean command.")

    clean_data_directory(log)


if __name__ == "__main__":
    clean()
