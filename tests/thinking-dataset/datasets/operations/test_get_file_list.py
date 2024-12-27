"""
@file tests/thinking_dataset/datasets/operations/test_get_file_list.py
@description Tests for GetFileList operation.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import pytest
from unittest.mock import MagicMock
from dotenv import load_dotenv
from thinking_dataset.datasets.operations.get_file_list import GetFileList

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
HF_ORGANIZATION = "DataTonic"
HF_DATASET = "cablegate-pdf-dataset"


class MockDatasetInfo:

    def __init__(self):
        self.siblings = [
            type('obj', (object, ), {'rfilename': 'file1.parquet'}),
            type('obj', (object, ), {'rfilename': 'file2.parquet'})
        ]


class MockDataTonic:

    def get_dataset_info(self, dataset_id=None):
        return MockDatasetInfo()

    def log_info(self, message):
        print(f"INFO: {message}")


@pytest.fixture
def mock_data_tonic():
    return MockDataTonic()


def test_get_file_list(mock_data_tonic):
    operation = GetFileList(mock_data_tonic)
    operation.log_info = MagicMock()

    file_list = operation.execute(HF_DATASET)
    assert len(file_list) == 2

    # Reflect the actual module name in the log message
    operation.log_info.assert_called_with("Dataset files: ["
                                          "<class 'test_get_file_list.obj'>, "
                                          "<class 'test_get_file_list.obj'>]")


if __name__ == "__main__":
    pytest.main()
