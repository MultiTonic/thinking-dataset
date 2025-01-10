"""
@file tests/thinking_dataset/datasets/operations/test_get_card_content.py
@description Tests for the GetCardContent operation in Thinking-Dataset Project
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from unittest.mock import patch, MagicMock
from huggingface_hub import DatasetInfo
from thinking_dataset.dataset.operations.get_card_content \
    import GetCardContent


def test_get_card_content():
    mock_data_tonic = MagicMock()
    operation = GetCardContent(mock_data_tonic)

    dataset_id = "test_dataset"
    mock_card_data = {"description": "Test Dataset Description"}
    mock_dataset_info = DatasetInfo(id=dataset_id, card_data=mock_card_data)

    with patch.object(mock_data_tonic,
                      'get_dataset_info',
                      return_value=mock_dataset_info):
        card_content = operation.execute(dataset_id)
        print(f"card_content: {card_content}")
        print(f"mock_card_data: {mock_card_data}")
        assert card_content.get('description') == mock_card_data['description']
        mock_data_tonic.get_dataset_info.assert_called_once_with(dataset_id)


if __name__ == "__main__":
    pytest.main()
