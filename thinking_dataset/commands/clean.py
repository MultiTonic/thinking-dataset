"""
@file thinking_dataset/commands/clean.py
@description Command to clean the data directory and other dynamic resources.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import shutil
import click
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve ROOT_DIR and DATA_DIR from environment variables
ROOT_DIR = os.path.expanduser(os.getenv("ROOT_DIR", "."))
DATA_DIR = os.getenv("DATA_DIR", "data")


def clean_data_directory():
    """
    Cleans the data directory and other dynamic resources.
    """
    base_dir_path = os.path.abspath(os.path.join(ROOT_DIR, DATA_DIR))

    if os.path.exists(base_dir_path):
        try:
            shutil.rmtree(base_dir_path)
            print(f"Removed directory: {base_dir_path}")
        except PermissionError as e:
            print(f"PermissionError: {e}")
    else:
        print(f"No directory found at {base_dir_path}")

    try:
        os.makedirs(base_dir_path)
        print(f"Created clean directory: {base_dir_path}")
    except PermissionError as e:
        print(f"PermissionError: {e}")


@click.command()
def clean():
    """
    Cleans the data directory and other dynamic resources.
    """
    clean_data_directory()


if __name__ == "__main__":
    clean()
