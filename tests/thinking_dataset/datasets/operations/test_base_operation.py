"""
@file tests/operations/test_base_operation.py
@description Unit tests for the BaseOperation class.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import unittest
import logging
from thinking_dataset.dataset.operations.operation import Operation


class MockOperation(Operation):
    """
    A mock class to test BaseOperation functionality.
    """

    def execute(self):
        """
        Mock execute method.
        """
        self.log_info("Executing mock operation.")


class TestBaseOperation(unittest.TestCase):
    """
    Unit tests for the BaseOperation class.
    """

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.INFO, force=True)

    def setUp(self):
        self.mock_data_tonic = "MockDataTonic"
        self.operation = MockOperation(self.mock_data_tonic)

    def test_initialization(self):
        """
        Test initialization of BaseOperation.
        """
        self.assertEqual(self.operation.data_tonic, self.mock_data_tonic)

    def test_log_info(self):
        """
        Test the log_info method.
        """
        with self.assertLogs(level='INFO') as log:
            self.operation.log_info("Test message.")
            self.assertIn("INFO:root:Test message.", log.output)

    def test_execute(self):
        """
        Test the execute method of the mock class.
        """
        with self.assertLogs(level='INFO') as log:
            self.operation.execute()
            self.assertIn("INFO:root:Executing mock operation.", log.output)


if __name__ == "__main__":
    unittest.main()
