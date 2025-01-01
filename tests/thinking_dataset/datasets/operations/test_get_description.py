"""
@file tests/thinking_dataset/datasets/operations/test_get_description.py
@description Tests for GetDescription operation.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from unittest.mock import MagicMock
from thinking_dataset.datasets.operations.get_description import GetDescription


class MockDatasetInfo:

    def __init__(self):
        self.card_data = {"description": "This is a test dataset."}


class MockDataTonic:

    def get_dataset_info(self, dataset_id=None):
        return MockDatasetInfo()

    def log_info(self, message):
        print(f"INFO: {message}")


@pytest.fixture
def mock_data_tonic():
    return MockDataTonic()


def test_get_description(mock_data_tonic):
    operation = GetDescription(mock_data_tonic)
    description = operation.execute()
    assert description == "This is a test dataset."

    operation.log_info = MagicMock()
    operation.execute()
    operation.log_info.assert_called_with(
        "Dataset description: This is a test dataset.")


if __name__ == "__main__":
    pytest.main()
