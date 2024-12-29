"""
@file tests/thinking_dataset/datasets/operations/test_get_tags.py
@description Tests for GetTags operation in Thinking-Dataset Project.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from unittest.mock import MagicMock
from thinking_dataset.datasets.operations.get_tags import GetTags


class MockDatasetInfo:
    """
    Mock class for DatasetInfo to be used in tests.
    """

    def __init__(self):
        self.tags = ["tag1", "tag2"]


class MockDataTonic:
    """
    Mock class for DataTonic to be used in tests.
    """

    def __init__(self):
        self.organization = "test_org"
        self.dataset = "test_dataset"

    def get_dataset_info(self, dataset_id=None):
        """
        Mock method to get dataset info.
        """
        return MockDatasetInfo()

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


def test_get_tags(mock_data_tonic):
    """
    Test the GetTags operation.
    """
    operation = GetTags(mock_data_tonic)
    tags = operation.execute("test_dataset")
    assert tags == ["tag1", "tag2"]

    # Checking if log_info was called
    operation.log_info = MagicMock()
    operation.execute("test_dataset")
    operation.log_info.assert_called_with("Dataset tags: ['tag1', 'tag2']")


if __name__ == "__main__":
    pytest.main()
