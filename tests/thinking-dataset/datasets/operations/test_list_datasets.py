"""
@file tests/operations/test_list_datasets.py
@description Unit tests for listing datasets in the thinking-dataset.
@version 1.0.0
@license MIT
@author Kara Rawson
@see https://github.com/MultiTonic/thinking-dataset
@see https://huggingface.co/DataTonic
"""

import os
import pytest
from unittest.mock import patch
from dotenv import load_dotenv
from loguru import logger
from thinking_dataset.tonics.data_tonic import DataTonic
from thinking_dataset.datasets.operations.list_datasets import ListDatasets
from thinking_dataset.datasets.dataset_info import DatasetInfo

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
HF_ORGANIZATION = "DataTonic"
HF_DATASET = "cablegate-pdf-dataset"


class MockDatasetInfo(DatasetInfo):
    """
    Mock class for DatasetInfo to be used in tests.
    """

    def __init__(self):
        # Initialize the base class
        super().__init__(data_tonic=None)
        # Set id and other necessary attributes
        self.id = f"{HF_ORGANIZATION}/{HF_DATASET}"
        self.tags = ["cleaned-text"]


def test_list_datasets():
    client = DataTonic(token=HF_TOKEN,
                       organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_datasets = [MockDatasetInfo()]

    with patch.object(ListDatasets(client),
                      'execute',
                      return_value=mock_datasets):
        list_datasets_operation = ListDatasets(client)
        datasets = list_datasets_operation.execute()
        logger.info(f"Listed datasets: {datasets}")
        assert len(datasets) > 0
        assert HF_ORGANIZATION in datasets[0].id


if __name__ == "__main__":
    pytest.main()
