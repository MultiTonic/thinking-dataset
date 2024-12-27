"""
@file thinking_dataset/tests/datasets/test_dataset_info.py
@description Tests for the DatasetInfo class in the Thinking Dataset Project.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from thinking_dataset.datasets.dataset_info import DatasetInfo


class MockDatasetInfo:
    """
    Mock class for DatasetInfo to be used in tests.
    """

    def __init__(self):
        self.card_data = {
            "configs": ["config1", "config2"],
            "description": "This is a test dataset.",
            "license": "MIT",
            "dataset_info": {
                "splits": ["train", "test", "validation"]
            }
        }


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


def test_get_configurations(mock_data_tonic):
    """
    Test the get_configurations method.
    """
    dataset_info = DatasetInfo(mock_data_tonic)
    configs = dataset_info.get_configurations()
    assert configs == ["config1", "config2"]


def test_get_description(mock_data_tonic):
    """
    Test the get_description method.
    """
    dataset_info = DatasetInfo(mock_data_tonic)
    description = dataset_info.get_description()
    assert description == "This is a test dataset."


def test_get_dataset_license(mock_data_tonic):
    """
    Test the get_dataset_license method.
    """
    dataset_info = DatasetInfo(mock_data_tonic)
    license_info = dataset_info.get_dataset_license()
    assert license_info == "MIT"


def test_get_dataset_split_information(mock_data_tonic):
    """
    Test the get_dataset_split_information method.
    """
    dataset_info = DatasetInfo(mock_data_tonic)
    splits = dataset_info.get_dataset_split_information()
    assert splits == ["train", "test", "validation"]


if __name__ == "__main__":
    pytest.main()
