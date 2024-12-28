"""
@file tests/thinking_dataset/datasets/test_dataset_downloads.py
@description Tests for the DatasetDownloads class in Thinking-Dataset Project.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from loguru import logger
from huggingface_hub import DatasetInfo
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
    print("HF_TOKEN, HF_DATASET, or HF_ORGANIZATION is not set. Please "
          "check your .env file.")


def test_dataset_download_url():
    client = DataTonic(token=HF_TOKEN,
                       organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        siblings=[MagicMock(rfilename='file.parquet')])
    with patch.object(client.downloads,
                      'get_dataset_download_urls',
                      return_value=[
                          file.rfilename for file in mock_dataset_info.siblings
                      ]):
        download_urls = client.downloads.get_dataset_download_urls()
        logger.info(f"Dataset download URLs: {download_urls}")
        assert len(download_urls) > 0


def test_dataset_permissions():
    client = DataTonic(token=HF_TOKEN,
                       organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(id=f"{HF_ORGANIZATION}/{HF_DATASET}",
                                    private=False)
    with patch.object(client.downloads,
                      'get_dataset_permissions',
                      return_value=mock_dataset_info.private):
        permissions = client.downloads.get_dataset_permissions()
        logger.info(f"Dataset permissions: {permissions}")
        assert permissions is False


if __name__ == "__main__":
    pytest.main()
