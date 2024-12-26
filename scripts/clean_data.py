"""
@file scripts/clean_data.py
@description Script to clean the data directory and other dynamic resources.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import shutil


def clean_data_directory():
    """
    Cleans the data directory and other dynamic resources.
    """
    data_directory = os.getenv("BASE_DIR", "data")
    
    if os.path.exists(data_directory):
        shutil.rmtree(data_directory)
        print(f"Removed directory: {data_directory}")
    else:
        print(f"No directory found at {data_directory}")

    os.makedirs(data_directory)
    print(f"Created clean directory: {data_directory}")


if __name__ == "__main__":
    clean_data_directory()
