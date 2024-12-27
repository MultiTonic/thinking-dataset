"""
@file tests/operations/test_get_download_size.py
@description Tests for GetDownloadSize operation in Thinking-Dataset Project.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from thinking_dataset.datasets.operations.get_download_size \
    import GetDownloadSize


class MockDatasetInfo:
    """
    Mock class for DatasetInfo to be used in tests.
    """

    def __init__(self):
        self.card_data = {"download_size": 1024}


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


def test_get_download_size(mock_data_tonic):
    """
    Test the GetDownloadSize operation.
    """
    operation = GetDownloadSize(mock_data_tonic)
    download_size = operation.execute()
    assert download_size == 1024


if __name__ == "__main__":
    pytest.main()
