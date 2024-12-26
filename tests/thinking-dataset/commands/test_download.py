"""
@file thinking_dataset/tests/commands/test_download.py
@description Tests for the download command in the Thinking Dataset Project.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from unittest.mock import patch
from rich.console import Console
from dotenv import load_dotenv
from thinking_dataset.commands.download import (
    load_env_variables, construct_paths, 
    validate_env_variables, download_files
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
    monkeypatch.setenv("HF_TOKEN", "test_token")
    monkeypatch.setenv("HF_DATASET", "test_dataset")
    monkeypatch.setenv("HF_ORGANIZATION", "test_organization")
    monkeypatch.setenv("ROOT_DIR", "/test/root/dir")
    monkeypatch.setenv("DATA_DIR", "test_data")

    env_vars = load_env_variables()
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

    raw_dir, processed_dir = construct_paths(root_dir, data_dir)
    expected_raw_dir = os.path.join(root_dir, data_dir, "raw", "cablegate")
    expected_processed_dir = os.path.join(root_dir, data_dir, 
                                          "processed", "cablegate")

    assert raw_dir == expected_raw_dir
    assert processed_dir == expected_processed_dir


def test_validate_env_variables():
    """
    Test the validate_env_variables function.
    """
    console = Console()

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

    assert validate_env_variables(valid_env_vars, console) is True
    assert validate_env_variables(invalid_env_vars, console) is False


def test_download_files(monkeypatch, tmp_path):
    """
    Test the download_files function.
    """
    env_vars = {
        "HF_TOKEN": "test_token",
        "HF_DATASET": "test_dataset",
        "HF_ORGANIZATION": "test_organization",
        "ROOT_DIR": str(tmp_path),
        "DATA_DIR": "test_data"
    }
    raw_dir = tmp_path / "raw" / "cablegate"
    console = Console()

    with patch("thinking_dataset.io.files.Files.ensure_directories") as mock_ensure, \
         patch("thinking_dataset.io.files.Files.get_file_path") as mock_get, \
         patch("huggingface_hub.HfApi.list_repo_files") as mock_list, \
         patch("huggingface_hub.hf_hub_download") as mock_download:

        mock_ensure.return_value = None
        mock_get.side_effect = lambda directory, filename: os.path.join(
            directory, filename)
        mock_list.return_value = [
            "train-00000-of-00001.parquet", "cleaned_data.parquet"]
        mock_download.side_effect = lambda *args, **kwargs: str(
            tmp_path / 'mock_file.parquet')

        download_files(env_vars, str(raw_dir), console)

        mock_ensure.assert_called_once_with([str(raw_dir)])
        mock_list.assert_called_once_with(
            repo_id="test_organization/test_dataset",
            token="test_token", repo_type="dataset")
        mock_download.assert_any_call(
            repo_id="test_organization/test_dataset",
            filename="train-00000-of-00001.parquet",
            local_dir=str(raw_dir), token="test_token",
            repo_type="dataset")
        mock_download.assert_any_call(
            repo_id="test_organization/test_dataset",
            filename="cleaned_data.parquet",
            local_dir=str(raw_dir), token="test_token",
            repo_type="dataset")


def test_download_command(monkeypatch, tmp_path):
    """
    Test the overall download command.
    """
    monkeypatch.setenv("HF_TOKEN", "test_token")
    monkeypatch.setenv("HF_DATASET", "test_dataset")
