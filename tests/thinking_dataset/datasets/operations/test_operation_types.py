"""
@file tests/thinking_dataset/datasets/operations/test_operation_types.py
@description Unit tests for the OperationTypes enum.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import unittest
from thinking_dataset.dataset.operations.operation_types import OperationTypes


class TestOperationTypes(unittest.TestCase):
    """
    Unit tests for the OperationTypes enum.
    """

    def test_enum_members(self):
        """
        Test that all enum members are correctly defined.
        """
        self.assertEqual(OperationTypes.GET_CARD_CONTENT.value,
                         "get_card_content")
        self.assertEqual(OperationTypes.GET_CONFIGURATION.value,
                         "get_configuration")
        self.assertEqual(OperationTypes.GET_DESCRIPTION.value,
                         "get_description")
        self.assertEqual(OperationTypes.GET_DOWNLOAD_SIZE.value,
                         "get_download_size")
        self.assertEqual(OperationTypes.GET_DOWNLOAD_URLS.value,
                         "get_download_urls")
        self.assertEqual(OperationTypes.GET_FILE_LIST.value, "get_file_list")
        self.assertEqual(OperationTypes.GET_LICENSE.value, "get_license")
        self.assertEqual(OperationTypes.GET_METADATA.value, "get_metadata")
        self.assertEqual(OperationTypes.GET_PERMISSIONS.value,
                         "get_permissions")
        self.assertEqual(OperationTypes.GET_SPLIT_INFORMATION.value,
                         "get_split_information")
        self.assertEqual(OperationTypes.GET_TAGS.value, "get_tags")
        self.assertEqual(OperationTypes.GET_INFO.value, "get_info")
        self.assertEqual(OperationTypes.LIST_DATASETS.value, "list_datasets")

    def test_enum_names(self):
        """
        Test that the enum member names are as expected.
        """
        self.assertTrue(hasattr(OperationTypes, "GET_CARD_CONTENT"))
        self.assertTrue(hasattr(OperationTypes, "GET_CONFIGURATION"))
        self.assertTrue(hasattr(OperationTypes, "GET_DESCRIPTION"))
        self.assertTrue(hasattr(OperationTypes, "GET_DOWNLOAD_SIZE"))
        self.assertTrue(hasattr(OperationTypes, "GET_DOWNLOAD_URLS"))
        self.assertTrue(hasattr(OperationTypes, "GET_FILE_LIST"))
        self.assertTrue(hasattr(OperationTypes, "GET_LICENSE"))
        self.assertTrue(hasattr(OperationTypes, "GET_METADATA"))
        self.assertTrue(hasattr(OperationTypes, "GET_PERMISSIONS"))
        self.assertTrue(hasattr(OperationTypes, "GET_SPLIT_INFORMATION"))
        self.assertTrue(hasattr(OperationTypes, "GET_TAGS"))
        self.assertTrue(hasattr(OperationTypes, "GET_INFO"))
        self.assertTrue(hasattr(OperationTypes, "LIST_DATASETS"))


if __name__ == "__main__":
    unittest.main()
