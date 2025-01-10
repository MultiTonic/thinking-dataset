"""
@file thinking_dataset/tests/datasets/test_base_dataset.py
@description Tests for the BaseDataset class in the Thinking Dataset Project.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from thinking_dataset.dataset.base_dataset import BaseDataset


class MockDataTonic:
    """
    Mock class for DataTonic to be used in tests.
    """

    def __init__(self):
        self.organization = "test_org"
        self.dataset = "test_dataset"

    def get_dataset_info(self, dataset_id):
        """
        Mock method to get dataset info.
        """
        return {
            "id":
            dataset_id,
            "siblings": [
                {
                    "rfilename": "file1.parquet"
                },
                {
                    "rfilename": "file2.parquet"
                },
            ],
            "private":
            False,
            "tags": ["tag1", "tag2"],
            "card_data": {
                "key": "value"
            },
        }

    def log_info(self, message):
        """
        Mock method to log info.
        """
        print(f"INFO: {message}")


@pytest.fixture
def mock_data_tonic():
    """
    Fixture to create a mock DataTonic instance.
    """
    return MockDataTonic()


def test_get_dataset_info(mock_data_tonic):
    """
    Test the get_dataset_info method.
    """
    base_dataset = BaseDataset(mock_data_tonic)
    dataset_info = base_dataset.get_path("test_id")
    assert dataset_info["id"] == "test_id"
    assert len(dataset_info["siblings"]) == 2
    assert dataset_info["siblings"][0]["rfilename"] == "file1.parquet"
    assert dataset_info["siblings"][1]["rfilename"] == "file2.parquet"


def test_log_info(mock_data_tonic):
    """
    Test the log_info method.
    """
    base_dataset = BaseDataset(mock_data_tonic)
    base_dataset.log_info("Test log message")
    assert True  # Assuming log_info method prints the message


if __name__ == "__main__":
    pytest.main()
