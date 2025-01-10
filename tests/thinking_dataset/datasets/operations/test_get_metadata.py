"""
@file tests/thinking_dataset/datasets/operations/test_get_metadata.py
@description Tests for the GetMetadata operation in Thinking-Dataset
@version 1.0.0
@license MIT
@param Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from unittest.mock import patch, MagicMock
from huggingface_hub import DatasetInfo
from thinking_dataset.dataset.operations.get_metadata import GetMetadata


def test_get_metadata():
    mock_data_tonic = MagicMock()
    operation = GetMetadata(mock_data_tonic)

    mock_dataset_info = DatasetInfo(id="test_dataset",
                                    description="Test dataset")

    with patch.object(mock_data_tonic,
                      'get_dataset_info',
                      return_value=mock_dataset_info):
        metadata = operation.execute()
        assert metadata.id == "test_dataset"
        assert metadata.description == "Test dataset"


if __name__ == "__main__":
    pytest.main()
