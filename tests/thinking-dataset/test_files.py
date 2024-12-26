"""
@file thinking_dataset/tests/test_files.py
@description Tests for the Files class in the Thinking Dataset Project.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import pytest
from thinking_dataset.files import Files


def test_ensure_directories(monkeypatch, tmp_path):
    """
    Test the ensure_directories method of the Files class.
    """
    files = Files(base_dir=tmp_path)
    files.ensure_directories()

    assert os.path.isdir(files.raw_dir)
    assert os.path.isdir(files.processed_dir)


def test_list_files(monkeypatch, tmp_path):
    """
    Test the list_files method of the Files class.
    """
    files = Files(base_dir=tmp_path)
    files.ensure_directories()

    # Create some dummy files
    raw_file = files.get_raw_file_path("test_raw.txt")
    processed_file = files.get_processed_file_path("test_processed.txt")

    with open(raw_file, "w") as f:
        f.write("raw")

    with open(processed_file, "w") as f:
        f.write("processed")

    assert "test_raw.txt" in files.list_files(files.raw_dir)
    assert "test_processed.txt" in files.list_files(files.processed_dir)


if __name__ == "__main__":
    pytest.main()
