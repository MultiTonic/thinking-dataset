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


def test_dataset_download_url():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        siblings=[MagicMock(rfilename='file.parquet')]
    )
    with patch.object(client.downloads, 'get_dataset_download_urls',
                      return_value=[file.rfilename for file in
                                    mock_dataset_info.siblings]):
        download_urls = client.downloads.get_dataset_download_urls()
        logger.info(f"Dataset download URLs: {download_urls}")
        assert len(download_urls) > 0


def test_dataset_permissions():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(id=f"{HF_ORGANIZATION}/{HF_DATASET}",
                                    private=False)
    with patch.object(client.downloads, 'get_dataset_permissions',
                      return_value=mock_dataset_info.private):
        permissions = client.downloads.get_dataset_permissions()
        logger.info(f"Dataset permissions: {permissions}")
        assert permissions is False


def test_dataset_file_list():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        siblings=[MagicMock(rfilename='README.md')]
    )
    with patch.object(client.downloads, 'get_dataset_file_list',
                      return_value=mock_dataset_info.siblings):
        file_list = client.downloads.get_dataset_file_list()
        logger.info(f"Dataset files: {file_list}")
        assert len(file_list) > 0


if __name__ == "__main__":
    pytest.main()