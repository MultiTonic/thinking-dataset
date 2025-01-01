"""
@file tests/thinking_dataset/datasets/operations/test_get_download_file.py
@description Tests for GetDownloadFile operation.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|thinking-dataset}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import pytest
from unittest.mock import patch
from dotenv import load_dotenv
from rich.console import Console
from thinking_dataset.datasets.operations.get_download_file \
    import GetDownloadFile

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
HF_ORGANIZATION = "DataTonic"
HF_DATASET = "cablegate-pdf-dataset"


class MockDataTonic:

    def log_info(self, message):
        print(f"INFO: {message}")


@pytest.fixture
def mock_data_tonic():
    return MockDataTonic()


@pytest.fixture
def get_download_file(mock_data_tonic):
    return GetDownloadFile(mock_data_tonic)


def test_execute_success(get_download_file):
    repo_id = "test-repo"
    filename = "test-file.parquet"
    local_dir = "test-local-dir"
    token = "test-token"
    console = Console()

    os.makedirs(local_dir, exist_ok=True)

    with patch(
            "thinking_dataset.datasets.operations.get_download_file."
            "hf_hub_download", ) as mock_hf_hub_download:
        mock_hf_hub_download.return_value = os.path.join(local_dir, filename)
        result = get_download_file.execute(repo_id, filename, local_dir, token,
                                           console)

        # Simulate the creation of the file by hf_hub_download
        open(mock_hf_hub_download.return_value, 'a').close()

        assert result is True
        assert os.path.exists(os.path.join(local_dir, filename))

    # Cleanup
    os.remove(os.path.join(local_dir, filename))
    os.rmdir(local_dir)


def test_execute_failure_permission_error(get_download_file):
    repo_id = "test-repo"
    filename = "test-file.parquet"
    local_dir = "test-local-dir"
    token = "test-token"
    console = Console()

    os.makedirs(local_dir, exist_ok=True)
    file_path = os.path.join(local_dir, filename)
    open(file_path, 'a').close()

    with patch("os.chmod", side_effect=PermissionError("Permission Denied")), \
         patch("thinking_dataset.datasets.operations.get_download_file."
               "hf_hub_download",
               return_value=True):
        result = get_download_file.execute(repo_id, filename, local_dir, token,
                                           console)
        assert result is False

    # Cleanup
    os.remove(file_path)
    os.rmdir(local_dir)


if __name__ == "__main__":
    pytest.main()
