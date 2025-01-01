"""
@file tests/thinking_dataset/datasets/operations/test_get_info.py
@description Tests for retrieving dataset information.
@version 1.0.0
@license MIT
@param Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import pytest
from unittest.mock import patch
from dotenv import load_dotenv
from loguru import logger
from thinking_dataset.tonics.data_tonic import DataTonic
from thinking_dataset.datasets.operations.get_info import GetInfo
from huggingface_hub.utils import RepositoryNotFoundError

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
HF_ORGANIZATION = "DataTonic"
HF_DATASET = "cablegate-pdf-dataset"


class MockResponse:
    """
    Mock class for the response to be used in tests.
    """

    def __init__(self, dataset_id):
        self.id = dataset_id
        self.card_data = {
            "download_size": 1024,
            "description": "This is a test dataset."
        }


def test_get_info():
    client = DataTonic(token=HF_TOKEN,
                       organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    dataset_id = f"{HF_ORGANIZATION}/{HF_DATASET}"
    mock_response = MockResponse(dataset_id)

    with patch.object(client.api, 'dataset_info', return_value=mock_response):
        get_info_operation = GetInfo(client)
        dataset_info = get_info_operation.execute(dataset_id)
        assert dataset_info.id == dataset_id
        assert dataset_info.card_data["download_size"] == 1024
        assert dataset_info.card_data[
            "description"] == "This is a test dataset."
        logger.info(f"Retrieved dataset info: {dataset_info.id}")


def test_get_info_repository_not_found():
    client = DataTonic(token=HF_TOKEN,
                       organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    dataset_id = f"{HF_ORGANIZATION}/non_existent_dataset"

    with patch.object(client.api, 'dataset_info') as mock_execute:
        mock_execute.side_effect = RepositoryNotFoundError(
            f"Repository not found for {dataset_id}")
        get_info_operation = GetInfo(client)
        with pytest.raises(RepositoryNotFoundError):
            get_info_operation.execute(dataset_id)
            logger.info(f"Error retrieving dataset info for {dataset_id}")


def test_logging_for_get_info():
    client = DataTonic(token=HF_TOKEN,
                       organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    dataset_id = f"{HF_ORGANIZATION}/{HF_DATASET}"
    mock_response = MockResponse(dataset_id)

    with patch.object(client.api, 'dataset_info', return_value=mock_response):
        get_info_operation = GetInfo(client)
        with patch.object(get_info_operation, 'log_info') as mock_log_info:
            get_info_operation.execute(dataset_id)
            mock_log_info.assert_called_with(
                "Retrieved dataset info: This is a test dataset.")
            # Add this line to output the calls made to log_info
            print(mock_log_info.mock_calls)


if __name__ == "__main__":
    pytest.main()
