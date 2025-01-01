"""
@file thinking_dataset/tests/commands/test_files.py
@description Tests for the Files class in the Thinking Dataset Project.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import pytest
from thinking_dataset.io.files import Files


def test_ensure_directories(monkeypatch, tmp_path):
    """
    Test the ensure_directories method of the Files class.
    """
    # Initialize the Files class with raw and processed directories
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    files = Files(raw_dir=raw_dir, processed_dir=processed_dir)
    files.touch()

    # Ensure the directories were created
    assert os.path.isdir(files.raw_dir)
    assert os.path.isdir(files.processed_dir)


def test_list_files(monkeypatch, tmp_path):
    """
    Test the list_files method of the Files class.
    """
    # Initialize the Files class with raw and processed directories
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    files = Files(raw_dir=raw_dir, processed_dir=processed_dir)
    files.touch()

    # Create some dummy files
    raw_file = files.get_path(files.raw_dir, "test_raw.txt")
    processed_file = files.get_path(files.processed_dir, "test_processed.txt")
    parquet_file = files.get_path(files.raw_dir, "test_file.parquet")

    with open(raw_file, "w") as f:
        f.write("raw")

    with open(processed_file, "w") as f:
        f.write("processed")

    with open(parquet_file, "w") as f:
        f.write("parquet")

    # List files in the directories and ensure they are present
    assert "test_raw.txt" in files.list(files.raw_dir)
    assert "test_processed.txt" in files.list(files.processed_dir)
    assert "test_file.parquet" in files.list(files.raw_dir)

    # List files with specific extension
    assert "test_file.parquet" in files.list(files.raw_dir,
                                             file_extension=".parquet")
    assert "test_raw.txt" not in files.list(files.raw_dir,
                                            file_extension=".parquet")
    assert "test_processed.txt" not in files.list(files.raw_dir,
                                                  file_extension=".parquet")


def test_list_files_with_extension_filter(monkeypatch, tmp_path):
    """
    Test the list_files method with a file extension filter.
    """
    # Initialize the Files class with raw and processed directories
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    files = Files(raw_dir=raw_dir, processed_dir=processed_dir)
    files.touch()

    # Create some dummy files with different extensions
    txt_file = files.get_path(files.raw_dir, "test_file.txt")
    parquet_file = files.get_path(files.raw_dir, "test_file.parquet")
    csv_file = files.get_path(files.raw_dir, "test_file.csv")

    with open(txt_file, "w") as f:
        f.write("txt")

    with open(parquet_file, "w") as f:
        f.write("parquet")

    with open(csv_file, "w") as f:
        f.write("csv")

    # List files with .parquet extension and ensure only .parquet files
    assert "test_file.parquet" in files.list(files.raw_dir,
                                             file_extension=".parquet")
    assert "test_file.txt" not in files.list(files.raw_dir,
                                             file_extension=".parquet")
    assert "test_file.csv" not in files.list(files.raw_dir,
                                             file_extension=".parquet")

    # List files with .txt extension and ensure only .txt files are listed
    assert "test_file.txt" in files.list(files.raw_dir, file_extension=".txt")
    assert "test_file.parquet" not in files.list(files.raw_dir,
                                                 file_extension=".txt")
    assert "test_file.csv" not in files.list(files.raw_dir,
                                             file_extension=".txt")

    # List files with .csv extension and ensure only .csv files are listed
    assert "test_file.csv" in files.list(files.raw_dir, file_extension=".csv")
    assert "test_file.txt" not in files.list(files.raw_dir,
                                             file_extension=".csv")
    assert "test_file.parquet" not in files.list(files.raw_dir,
                                                 file_extension=".csv")


if __name__ == "__main__":
    pytest.main()
