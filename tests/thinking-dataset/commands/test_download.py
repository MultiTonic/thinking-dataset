"""
@file thinking_dataset/tests/commands/test_download.py
@description Tests for the download command in the Thinking Dataset Project.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from rich.console import Console
from dotenv import load_dotenv
from thinking_dataset.commands.download import (
    load_env_variables, construct_paths,
    validate_env_variables
)
import os


# Load environment variables from .env file
load_dotenv()

# Retrieve ROOT_DIR and DATA_DIR from environment variables
ROOT_DIR = os.path.expanduser(os.getenv("ROOT_DIR", "."))
DATA_DIR = os.getenv("DATA_DIR", "data")


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

    # Assert the values to ensure correctness
    assert env_vars["HF_TOKEN"] == "test_token"
    assert env_vars["HF_DATASET"] == "test_dataset"
    assert env_vars["HF_ORGANIZATION"] == "test_organization"
    assert env_vars["ROOT_DIR"] == "/test/root/dir"
    assert env_vars["DATA_DIR"] == "test_data"


def test_construct_paths():
    """
    Test the construct_paths function.
    """
    root_dir = "/test/root/dir"
    data_dir = "test_data"

    # Construct paths for raw and processed data
    raw_dir, processed_dir = construct_paths(root_dir, data_dir)
    expected_raw_dir = os.path.join(root_dir, data_dir, "raw", "cablegate")
    expected_processed_dir = os.path.join(
        root_dir, data_dir, "processed", "cablegate"
    )

    # Assert the constructed paths to ensure correctness
    assert raw_dir == expected_raw_dir
    assert processed_dir == expected_processed_dir


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

    # Validate environment variables and assert correctness
    assert validate_env_variables(valid_env_vars, console) is True
    assert validate_env_variables(invalid_env_vars, console) is False


if __name__ == "__main__":
    pytest.main()
