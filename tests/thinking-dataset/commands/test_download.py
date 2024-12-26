"""
@file thinking_dataset/tests/commands/test_download.py
@description Tests for the download command in the Thinking Dataset Project.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from unittest.mock import patch
from dotenv import load_dotenv
from click.testing import CliRunner
from thinking_dataset.main import cli


# Load environment variables from .env file
load_dotenv()


def test_download_function(monkeypatch):
    mock_urls = ['mock_url.parquet']

    with patch('thinking_dataset.commands.download.DataTonic') \
            as MockDataTonic:
        mock_client = MockDataTonic.return_value
        mock_client.downloads.get_dataset_download_urls.return_value = (
            mock_urls
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['download'])

        assert result.exit_code == 0
        assert "Downloading Cablegate dataset..." in result.output
        assert "Downloaded mock_url.parquet to data" in result.output
        assert "raw/cablegate\\mock_url.parquet" in result.output
        assert "Downloaded 1 files to data\\raw/cablegate" in result.output


if __name__ == "__main__":
    pytest.main()
