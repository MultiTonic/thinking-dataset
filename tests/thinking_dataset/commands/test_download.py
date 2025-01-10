"""
@file thinking_dataset/tests/commands/test_download.py
@description Tests for the download command in the Thinking Dataset Project.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
import os
import io
import pytest
from dotenv import load_dotenv
from unittest.mock import patch
from rich.console import Console
from contextlib import redirect_stdout
from thinking_dataset.tonics.data_tonic \
    import DataTonic
from thinking_dataset.commands.download \
    import (load_env_variables,
            construct_paths,
            validate_env_variables,
            download_dataset)
from thinking_dataset.dataset.operations.get_download_urls \
    import GetDownloadUrls
from thinking_dataset.dataset.operations.get_download_file \
    import GetDownloadFile

# Load environment variables from .env file
load_dotenv()

# Retrieve ROOT_DIR and DATA_DIR from environment variables
ROOT_DIR = os.path.expanduser(os.getenv("ROOT_DIR", "."))
DATA_DIR = os.getenv("DATA_DIR", "data")

# Add logging to check if environment variables are loaded correctly
print(f"ROOT_DIR: {ROOT_DIR}")
print(f"DATA_DIR: {DATA_DIR}")


def test_load_env_variables(monkeypatch):
    """
    Test the load_env_variables function.
    """
    # Set environment variables for testing
    monkeypatch.setenv("HF_TOKEN", "test_token")
    monkeypatch.setenv("HF_DATASET", "test_dataset")
    monkeypatch.setenv("HF_ORGANIZATION", "test_organization")
    monkeypatch.setenv("ROOT_DIR", "/test/root/dir")
    monkeypatch.setenv("DATA_DIR", "test_data")

    # Load the environment variables
    env_vars = load_env_variables()

    # Normalize paths to handle drive letters on Windows
    root_dir = os.path.splitdrive(env_vars["ROOT_DIR"])[1].replace(
        "\\", "/").lower()
    expected_root_dir = "/test/root/dir".replace("\\", "/").lower()

    # Assert the values to ensure correctness
    assert env_vars["HF_TOKEN"] == "test_token"
    assert env_vars["HF_DATASET"] == "test_dataset"
    assert env_vars["HF_ORGANIZATION"] == "test_organization"
    assert root_dir == expected_root_dir
    assert env_vars["DATA_DIR"] == "test_data"


def test_construct_paths():
    """
    Test the construct_paths function.
    """
    root_dir = "/test/root/dir"
    data_dir = "test_data"

    # Construct paths for raw and process data
    raw_dir, process_dir = construct_paths(root_dir, data_dir)
    expected_raw_dir = os.path.join(root_dir, data_dir,
                                    "raw").replace("\\", "/").lower()
    expected_process_dir = os.path.join(root_dir, data_dir,
                                        "process").replace("\\", "/").lower()

    # Normalize paths to handle drive letters on Windows
    raw_dir = os.path.splitdrive(raw_dir)[1].replace("\\", "/").lower()
    process_dir = os.path.splitdrive(process_dir)[1].replace("\\", "/").lower()

    # Assert the constructed paths to ensure correctness
    assert raw_dir == expected_raw_dir
    assert process_dir == expected_process_dir


def test_validate_env_variables():
    """
    Test the validate_env_variables function.
    """
    console = Console()

    # Define valid and invalid environment variables for testing
    valid_env_vars = {
        "HF_TOKEN": "test_token",
        "HF_DATASET": "test_dataset",
        "HF_ORGANIZATION": "test_organization",
        "ROOT_DIR": "/test/root/dir",
        "DATA_DIR": "test_data"
    }

    invalid_env_vars = {
        "HF_TOKEN": None,
        "HF_DATASET": "test_dataset",
        "HF_ORGANIZATION": "test_organization",
        "ROOT_DIR": "/test/root/dir",
        "DATA_DIR": "test_data"
    }

    # Add logging to see what gets validated
    print(f"Valid env vars: {valid_env_vars}")
    print(f"Invalid env vars: {invalid_env_vars}")

    # Suppress the output of the invalid test case
    with io.StringIO() as buf, redirect_stdout(buf):
        assert validate_env_variables(valid_env_vars, console) is True
        assert validate_env_variables(invalid_env_vars, console) is False


def test_download_dataset(monkeypatch):
    """
    Test the download_dataset function.
    """
    console = Console()

    # Set environment variables for testing
    monkeypatch.setenv("HF_TOKEN", "test_token")
    monkeypatch.setenv("HF_DATASET", "test_dataset")
    monkeypatch.setenv("HF_ORGANIZATION", "test_organization")
    env_vars = load_env_variables()

    dataset_id = f"{env_vars['HF_ORGANIZATION']}/{env_vars['HF_DATASET']}"
    download_dir = "test-download-dir"
    os.makedirs(download_dir, exist_ok=True)

    mock_urls = ["file1.parquet", "file2.parquet"]

    datatonic = DataTonic(read_token=env_vars['HF_TOKEN'])

    with patch.object(GetDownloadUrls, 'execute', return_value=mock_urls):
        with patch.object(GetDownloadFile, 'execute', return_value=True):
            # Mock the creation of files to simulate a successful download
            for file in mock_urls:
                open(os.path.join(download_dir, file), 'a').close()

            result = download_dataset(datatonic, env_vars['HF_TOKEN'],
                                      dataset_id, download_dir, console)
            assert result is True

            # Additional assertion and logging to verify behavior
            downloaded_files = os.listdir(download_dir)
            for file in mock_urls:
                assert file in downloaded_files

    # Clean up the directory after test
    for file in mock_urls:
        os.remove(os.path.join(download_dir, file))
    os.rmdir(download_dir)


if __name__ == "__main__":
    pytest.main()
