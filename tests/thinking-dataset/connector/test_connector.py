"""
@file thinking_dataset/tests/connectors/test_connector.py
@description Tests for the Connector class in the Thinking Dataset Project.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from unittest.mock import patch
from thinking_dataset.connectors.connector import Connector


class MockHfApi:
    """
    Mock class for HfApi to be used in tests.
    """

    def __init__(self, token):
        self.token = token

    def whoami(self):
        """
        Mock method to get information about the authenticated user.
        """
        return {"name": "test_user"}

    def list_datasets(self, author=None, search=None):
        """
        Mock method to list datasets.
        """
        return ["dataset1", "dataset2"]

    def dataset_info(self, dataset_id):
        """
        Mock method to get dataset info.
        """
        return {"id": dataset_id, "info": "test_info"}


@pytest.fixture
def mock_connector():
    """
    Fixture to create a mock Connector instance.
    """
    with patch('thinking_dataset.connectors.connector.HfApi', new=MockHfApi):
        return Connector(token="test_token")


def test_get_whoami(mock_connector):
    """
    Test the get_whoami method.
    """
    user_info = mock_connector.get_whoami()
    assert user_info == {"name": "test_user"}


def test_list_datasets(mock_connector):
    """
    Test the list_datasets method.
    """
    datasets = mock_connector.list_datasets()
    assert datasets == ["dataset1", "dataset2"]


def test_get_dataset_info(mock_connector):
    """
    Test the get_dataset_info method.
    """
    dataset_info = mock_connector.get_dataset_info("test_dataset_id")
    assert dataset_info == {"id": "test_dataset_id", "info": "test_info"}


if __name__ == "__main__":
    pytest.main()
