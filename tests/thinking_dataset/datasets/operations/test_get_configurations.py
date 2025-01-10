"""
@file tests/thinking_dataset/datasets/operations/test_get_configuration.py
@description Tests for GetConfiguration operation.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from unittest.mock import MagicMock
from thinking_dataset.dataset.operations.get_configuration \
    import GetConfiguration


class MockDatasetInfo:
    """
    Mock class for DatasetInfo to be used in tests.
    """

    def __init__(self):
        self.card_data = {"configs": ["config1", "config2"]}


class MockDataTonic:
    """
    Mock class for DataTonic to be used in tests.
    """

    def get_dataset_info(self):
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


def test_get_configuration(mock_data_tonic):
    """
    Test the GetConfiguration operation.
    """
    operation = GetConfiguration(mock_data_tonic)
    configs = operation.execute()
    assert configs == ["config1", "config2"]

    # Checking if log_info was called
    operation.log_info = MagicMock()
    operation.execute()
    operation.log_info.assert_called_with(
        "Dataset configurations: ['config1', 'config2']")


if __name__ == "__main__":
    pytest.main()
