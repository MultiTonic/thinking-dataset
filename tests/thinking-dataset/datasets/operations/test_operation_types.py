"""
@file tests/operations/test_operation_types.py
@description Unit tests for the OperationTypes enum.
@version 1.0.0
@license MIT
@author Kara Rawson
@see https://github.com/MultiTonic/thinking-dataset
@see https://huggingface.co/DataTonic
"""

import unittest
from thinking_dataset.datasets.operations.operation_types import OperationTypes


class TestOperationTypes(unittest.TestCase):
    """
    Unit tests for the OperationTypes enum.
    """

    def test_enum_members(self):
        """
        Test that all enum members are correctly defined.
        """
        self.assertEqual(OperationTypes.LIST_ORGANIZATION_DATASETS.value,
                         "list_organization_datasets")
        self.assertEqual(OperationTypes.GET_DATASET_METADATA.value,
                         "get_dataset_metadata")
        self.assertEqual(OperationTypes.GET_DATASET_TAGS.value,
                         "get_dataset_tags")
        self.assertEqual(OperationTypes.GET_DATASET_CARD_CONTENT.value,
                         "get_dataset_card_content")

    def test_enum_names(self):
        """
        Test that the enum member names are as expected.
        """
        self.assertTrue(hasattr(OperationTypes, "LIST_ORGANIZATION_DATASETS"))
        self.assertTrue(hasattr(OperationTypes, "GET_DATASET_METADATA"))
        self.assertTrue(hasattr(OperationTypes, "GET_DATASET_TAGS"))
        self.assertTrue(hasattr(OperationTypes, "GET_DATASET_CARD_CONTENT"))


if __name__ == "__main__":
    unittest.main()
