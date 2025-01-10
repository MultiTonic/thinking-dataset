"""
@file tests/thinking_dataset/datasets/operations/test_get_download_urls.py
@description Tests for GetDownloadUrls operation.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import pytest
from unittest.mock import MagicMock
from dotenv import load_dotenv
from thinking_dataset.dataset.operations.get_download_urls \
    import GetDownloadUrls

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
HF_ORGANIZATION = "DataTonic"
HF_DATASET = "cablegate-pdf-dataset"
HF_DATASET_TYPE = "pdf"


class MockDatasetInfo:

    def __init__(self):
        self.siblings = [
            type('obj', (object, ), {'rfilename': f'file1.{HF_DATASET_TYPE}'}),
            type('obj', (object, ), {'rfilename': f'file2.{HF_DATASET_TYPE}'})
        ]


class MockDataTonic:
    HF_DATASET_TYPE = HF_DATASET_TYPE

    def get_dataset_info(self, dataset_id=None):
        return MockDatasetInfo()

    def log_info(self, message):
        print(f"INFO: {message}")


@pytest.fixture
def mock_data_tonic():
    return MockDataTonic()


def test_get_download_urls(mock_data_tonic):
    operation = GetDownloadUrls(mock_data_tonic)
    operation.log_info = MagicMock()

    download_urls = operation.execute(HF_DATASET)
    assert len(download_urls) == 2
    assert all(url.endswith(f'.{HF_DATASET_TYPE}') for url in download_urls)

    operation.log_info.assert_called_with(f"Dataset download URLs: ["
                                          f"'file1.{HF_DATASET_TYPE}', "
                                          f"'file2.{HF_DATASET_TYPE}']")


if __name__ == "__main__":
    pytest.main()
