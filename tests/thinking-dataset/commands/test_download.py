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
from unittest.mock import patch
from dotenv import load_dotenv
from click.testing import CliRunner
from thinking_dataset.main import cli
import os

# Load environment variables from .env file
load_dotenv()


def test_download_function(monkeypatch, tmp_path):
    """
    Test the download function.
    """
    mock_urls = [
        'train-00000-of-00001.parquet',  # Example filename
        'cleaned_data.parquet'
    ]

    with patch('thinking_dataset.tonics.data_tonic.DataTonic') as \
            MockDataTonic, patch('huggingface_hub.hf_hub_download') as \
            mock_download:
        
        # Mock the return value of get_dataset_download_urls
        mock_client = MockDataTonic.return_value
        mock_client.downloads.get_dataset_download_urls.return_value = \
            mock_urls
        
        # Ensure the mock hf_hub_download does not make real network requests
        mock_download.side_effect = lambda *args, **kwargs: str(
            tmp_path / 'mock_file.parquet')

        runner = CliRunner()
        result = runner.invoke(cli, ['download'])

        expected_output_path = os.path.join("data", "raw")

        assert result.exit_code == 0
        assert "Downloading Cablegate dataset..." in result.output
        assert all(
            f"Downloaded {url}" in result.output
            for url in mock_urls
        )
        assert f"Downloaded {len(mock_urls)} files to " \
               f"{expected_output_path}".replace("\\", "/") in result.output. \
               replace("\\", "/")


if __name__ == "__main__":
    pytest.main()
