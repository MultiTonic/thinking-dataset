"""
@file tests/thinking_dataset/datasets/operations/test_get_split_information.py
@description Tests for GetSplitInformation operation.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from unittest.mock import MagicMock
from thinking_dataset.dataset.operations.get_split_information \
    import GetSplitInformation


class MockDatasetInfo:

    def __init__(self):
        self.card_data = {
            "dataset_info": {
                "splits": ["train", "test", "validation"]
            }
        }


class MockDataTonic:

    def get_dataset_info(self, dataset_id=None):
        return MockDatasetInfo()

    def log_info(self, message):
        print(f"INFO: {message}")


@pytest.fixture
def mock_data_tonic():
    return MockDataTonic()


def test_get_split_information(mock_data_tonic):
    operation = GetSplitInformation(mock_data_tonic)
    splits = operation.execute()
    assert splits == ["train", "test", "validation"]

    operation.log_info = MagicMock()
    operation.execute()
    operation.log_info.assert_called_with(
        "Dataset splits: ['train', 'test', 'validation']")


if __name__ == "__main__":
    pytest.main()
