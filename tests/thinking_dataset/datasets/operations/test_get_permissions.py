"""
@file tests/thinking_dataset/datasets/operations/test_get_permissions.py
@description Tests for the GetPermissions operation in Thinking-Dataset Project
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from unittest.mock import patch, MagicMock
from huggingface_hub import DatasetInfo
from thinking_dataset.dataset.operations.get_permissions import GetPermissions


def test_get_permissions():
    mock_data_tonic = MagicMock()
    operation = GetPermissions(mock_data_tonic)

    dataset_id = "test_dataset"
    mock_dataset_info = DatasetInfo(id=dataset_id, private=True)

    with patch.object(mock_data_tonic,
                      'get_dataset_info',
                      return_value=mock_dataset_info):
        permissions = operation.execute(dataset_id)
        assert permissions is True

    mock_dataset_info.private = False
    with patch.object(mock_data_tonic,
                      'get_dataset_info',
                      return_value=mock_dataset_info):
        permissions = operation.execute(dataset_id)
        assert permissions is False


if __name__ == "__main__":
    pytest.main()
