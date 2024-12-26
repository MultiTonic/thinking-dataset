"""
@file thinking_dataset/commands/clean.py
@description Command to clean the data directory and other dynamic resources.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import shutil
import click
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve BASE_DIR from environment variables, defaulting to "data"
BASE_DIR = os.getenv("BASE_DIR", "data")


def clean_data_directory():
    """
    Cleans the data directory and other dynamic resources.
    """
    if os.path.exists(BASE_DIR):
        shutil.rmtree(BASE_DIR)
        print(f"Removed directory: {BASE_DIR}")
    else:
        print(f"No directory found at {BASE_DIR}")

    os.makedirs(BASE_DIR)
    print(f"Created clean directory: {BASE_DIR}")


@click.command()
def clean():
    """
    Cleans the data directory and other dynamic resources.
    """
    clean_data_directory()
