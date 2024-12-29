"""
@file tests/thinking_dataset/downloads/test_dataset_downloads.py
@description Tests for the DatasetDownloads class in Thinking-Dataset Project.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|thinking-dataset}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
import os
import pytest
from unittest.mock import patch
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from thinking_dataset.datasets.dataset_downloads import DatasetDownloads
from thinking_dataset.datasets.operations.get_download_urls \
    import GetDownloadUrls
from thinking_dataset.datasets.operations.get_download_file \
    import GetDownloadFile
from thinking_dataset.tonics.data_tonic import DataTonic

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
HF_ORGANIZATION = "DataTonic"
HF_DATASET = "cablegate-pdf-dataset"

# Add logging to check if environment variables are loaded correctly
logger.info(f"HF_TOKEN: {HF_TOKEN}")
logger.info(f"HF_ORGANIZATION: {HF_ORGANIZATION}")
logger.info(f"HF_DATASET: {HF_DATASET}")

if not HF_TOKEN or not HF_DATASET or not HF_ORGANIZATION:
    print("HF_TOKEN, HF_DATASET, or HF_ORGANIZATION is not set. "
          "Please check your .env file.")


@pytest.fixture
def dataset_downloads():
    connector = DataTonic(token=HF_TOKEN,
                          organization=HF_ORGANIZATION,
                          dataset=HF_DATASET)
    return DatasetDownloads(connector=connector, token=HF_TOKEN)


def test_download_dataset(dataset_downloads):
    dataset_id = "test-dataset-id"
    download_dir = "test-download-dir"
    console = Console()

    # Ensure the directory exists
    os.makedirs(download_dir, exist_ok=True)

    mock_urls = ["file1.parquet", "file2.parquet"]

    with patch.object(GetDownloadUrls, 'execute', return_value=mock_urls):
        with patch.object(GetDownloadFile, 'execute', return_value=True):
            # Mock the creation of files to simulate a successful download
            for file in mock_urls:
                open(os.path.join(download_dir, file), 'a').close()

            result = dataset_downloads.download_dataset(
                dataset_id, download_dir, console)
            logger.info(f"Download result: {result}")
            assert result is True

            # Additional assertion and logging to verify behavior
            logger.info(f"Expected files: {', '.join(mock_urls)}")
            downloaded_files = os.listdir(download_dir)
            logger.info(f"Downloaded files: {', '.join(downloaded_files)}")

            for file in mock_urls:
                assert file in downloaded_files

    # Clean up the directory after test
    for file in mock_urls:
        os.remove(os.path.join(download_dir, file))
    os.rmdir(download_dir)


if __name__ == "__main__":
    pytest.main()
