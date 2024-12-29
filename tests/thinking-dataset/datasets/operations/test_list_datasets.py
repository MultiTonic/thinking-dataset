"""
@file tests/thinking_dataset/datasets/operations/test_list_datasets.py
@description Unit tests for listing datasets in the thinking-dataset.
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
from thinking_dataset.datasets.operations.list_datasets import ListDatasets
from thinking_dataset.utilities.text_utils import TextUtils

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
HF_ORGANIZATION = "DataTonic"
HF_DATASET = "cablegate-pdf-dataset"


class MockDataset:
    """
    Mock class for Dataset to be used in tests.
    """

    def __init__(self):
        self.id = f"{HF_ORGANIZATION}/{HF_DATASET}"
        self.tags = ["cleaned-text"]


def test_list_datasets():
    client = DataTonic(token=HF_TOKEN,
                       organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_datasets = [MockDataset()]

    with patch.object(client.api, 'list_datasets', return_value=mock_datasets):
        list_datasets_operation = ListDatasets(client)
        datasets = list_datasets_operation.execute()
        truncated_datasets = TextUtils.truncate_text(str(datasets))
        logger.info(f"Listed datasets: {truncated_datasets}")
        assert len(datasets) > 0
        assert HF_ORGANIZATION in datasets[0].id


if __name__ == "__main__":
    pytest.main()
