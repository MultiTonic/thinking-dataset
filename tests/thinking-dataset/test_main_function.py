"""
@file thinking_dataset/tests/test_main_function.py
@description High-level tests for the main function in the Thinking Dataset.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from click.testing import CliRunner
from thinking_dataset.main import cli

# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_datonics():
    with patch('thinking_dataset.commands.download.DataTonic',
               new=MagicMock()):
        yield


def test_main_function(monkeypatch, runner, mock_datonics):
    # Mock download_dataset to simulate successful download
    with patch('thinking_dataset.commands.download.download_dataset',
               return_value=True):
        runner = CliRunner()
        result = runner.invoke(cli, ['download'])

        assert result.exit_code == 0
        assert "Loaded environment variables" in result.output
        assert "Set Hugging Face cache directory" in result.output
        assert "Constructed paths" in result.output
        assert "Downloaded all datasetfiles to" in result.output


def test_clean_function(monkeypatch, runner):
    result = runner.invoke(cli, ['clean'])

    assert result.exit_code == 0
    assert "Removed directory" in result.output or \
           "No directory found" in result.output
    assert "Created clean directory" in result.output


def test_load_function(monkeypatch, runner):
    # Mock the Files class methods to avoid actual file system operations
    with patch('thinking_dataset.commands.load.Files.list_files',
               return_value=['test_file.parquet']), \
         patch('thinking_dataset.commands.load.Files.get_file_path',
               side_effect=lambda dir, fname: f"{dir}/{fname}"), \
         patch('thinking_dataset.commands.load.pd.read_parquet',
               return_value=MagicMock()), \
         patch('thinking_dataset.commands.load.pd.DataFrame.to_sql',
               return_value=True):

        result = runner.invoke(cli, ['load'])

        assert result.exit_code == 0
        assert "Successfully loaded dataset files into the database." \
            in result.output


if __name__ == "__main__":
    pytest.main()
