"""
@file tests/scripts/test_clean_pycache_and_pyc.py
@description Unit tests for the clean_pycache_and_pyc script.
@version 1.0.0
@license MIT
author Kara Rawson
@see https://github.com/MultiTonic/thinking-dataset
"""

import unittest
from unittest.mock import patch
import os
from scripts.clean_pycache_and_pyc \
    import clean_pycache_and_pyc, find_duplicate_test_files


class TestCleanPycacheAndPyc(unittest.TestCase):

    @patch('scripts.clean_pycache_and_pyc.os.walk')
    @patch('scripts.clean_pycache_and_pyc.os.remove')
    def test_clean_pycache_and_pyc(self, mock_remove, mock_walk):
        mock_walk.return_value = [('/some/path', ('dir1', 'dir2'),
                                   ('__pycache__', 'file1.pyc')),
                                  ('/some/path/dir1', (), ('file2.pyc', ))]
        clean_pycache_and_pyc('/some/path')
        self.assertEqual(mock_remove.call_count, 2)

    @patch('scripts.clean_pycache_and_pyc.os.walk')
    def test_find_duplicate_test_files(self, mock_walk):
        mock_walk.return_value = [('/some/path', ('dir1', 'dir2'),
                                   ('test_file1.py', 'test_file2.py')),
                                  ('/some/path/dir1', (), ('test_file1.py', ))]
        duplicates = find_duplicate_test_files('/some/path', 'test_file1.py')
        expected_duplicate1 = os.path.normpath('/some/path/test_file1.py')
        expected_duplicate2 = os.path.normpath('/some/path/dir1/test_file1.py')
        normalized_duplicates = [os.path.normpath(path) for path in duplicates]
        self.assertIn(expected_duplicate1, normalized_duplicates)
        self.assertIn(expected_duplicate2, normalized_duplicates)


if __name__ == "__main__":
    unittest.main()
