"""
@file tests/thinking_dataset/tonics/test_data_tonic.py
@description Tests for the DataTonic class in the Thinking Dataset Project.
@version 1.0.0
@license MIT
@param Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
import pytest
from unittest.mock import MagicMock, patch
from thinking_dataset.dataset.operations.get_configuration \
    import GetConfiguration
from thinking_dataset.dataset.operations.get_download_urls \
    import GetDownloadUrls
from thinking_dataset.dataset.operations.get_info import GetInfo

HF_TOKEN = "your_hf_token"
HF_ORGANIZATION = "your_hf_organization"
HF_DATASET = "your_hf_dataset"


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
        self.siblings = [
            MagicMock(rfilename="file1.parquet"),
            MagicMock(rfilename="file2.parquet"),
        ]


class MockDataTonic:
    """
    Mock class for DataTonic to be used in tests.
    """

    def __init__(self):
        self.organization = "test_org"
        self.dataset = "test_dataset"
        self.HF_DATASET_TYPE = "parquet"
        self.api = MagicMock()  # Adding a mock api attribute

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
    operation = GetConfiguration(mock_data_tonic)
    configs = operation.execute()
    assert configs == ["config1", "config2"]

    # Checking if log_info was called
    operation.log_info = MagicMock()
    operation.execute()
    operation.log_info.assert_called_with(
        "Dataset configurations: ['config1', 'config2']")


def test_get_download_urls(mock_data_tonic):
    """
    Test the GetDownloadUrls operation.
    """
    operation = GetDownloadUrls(mock_data_tonic)
    urls = operation.execute("test_dataset")
    assert urls == ["file1.parquet", "file2.parquet"]

    # Checking if log_info was called
    operation.log_info = MagicMock()
    operation.execute("test_dataset")
    operation.log_info.assert_called_with(
        "Dataset download URLs: ['file1.parquet', 'file2.parquet']")


def test_get_info(mock_data_tonic):
    """
    Test the GetInfo operation.
    """
    mock_data_tonic.api.dataset_info = MagicMock(
        return_value=MockDatasetInfo())
    operation = GetInfo(mock_data_tonic)

    with patch.object(operation, 'log_info') as mock_log_info:
        dataset_info = operation.execute("test_dataset")
        assert dataset_info.card_data[
            "description"] == "This is a test dataset."

        # Checking if log_info was called
        mock_log_info.assert_called_with(
            "Retrieved dataset info: This is a test dataset.")


if __name__ == "__main__":
    pytest.main()
