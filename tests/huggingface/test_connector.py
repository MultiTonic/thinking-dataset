import os
import pytest
from unittest.mock import patch
from dotenv import load_dotenv
from loguru import logger
from huggingface_hub import DatasetInfo
from thinking_dataset.connector import Connector

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
HF_USER = os.getenv("HF_USER")
HF_ORGANIZATION = "DataTonic"
HF_DATASET = "cablegate-pdf-dataset"


def test_hf_connection():
    connector = Connector(token=HF_TOKEN)
    with patch.object(connector.api, 'whoami', return_value={'name': HF_USER}):
        hf_info = connector.get_whoami()
        logger.info(f"Connected to Hugging Face as: {hf_info['name']}")
        assert hf_info is not None
        assert "name" in hf_info


def test_list_datasets():
    connector = Connector(token=HF_TOKEN)
    mock_datasets = [{'id': f"{HF_ORGANIZATION}/{HF_DATASET}"}]

    with patch.object(connector.api, 'list_datasets',
                      return_value=mock_datasets):
        datasets = connector.list_datasets(author=HF_ORGANIZATION)
        logger.info(f"Datasets listed: {datasets}")
        assert datasets is not None
        assert len(datasets) > 0


def test_get_dataset_info():
    connector = Connector(token=HF_TOKEN)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", private=False, downloads=34,
        last_modified=None, tags=['cleaned-text']
    )

    with patch.object(connector.api, 'dataset_info',
                      return_value=mock_dataset_info):
        dataset_info = connector.get_dataset_info(HF_DATASET)
        logger.info(f"Dataset info: {dataset_info}")
        assert dataset_info is not None
        assert hasattr(dataset_info, "id")
        assert hasattr(dataset_info, "private")
        assert hasattr(dataset_info, "downloads")
        assert hasattr(dataset_info, "last_modified")
        assert hasattr(dataset_info, "tags")


if __name__ == "__main__":
    pytest.main()
