"""
@file thinking_dataset/tests/commands/test_load.py
@description Tests for the load command in the Thinking Dataset Project.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from click.testing import CliRunner
from thinking_dataset.main import cli
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve ROOT_DIR and DATA_DIR from environment variables
ROOT_DIR = os.path.expanduser(os.getenv("ROOT_DIR", "."))
DATA_DIR = os.getenv("DATA_DIR", "data")


def test_load_function(monkeypatch):
    # Mock the Files class methods to avoid actual file system operations
    with patch('thinking_dataset.commands.load.Files.list_files',
               return_value=['test_file.parquet']), \
         patch('thinking_dataset.commands.load.Files.get_file_path',
               side_effect=lambda dir, fname: f"{dir}/{fname}"), \
         patch('thinking_dataset.commands.load.pd.read_parquet',
               return_value=MagicMock()), \
         patch('thinking_dataset.commands.load.pd.DataFrame.to_sql',
               return_value=True):

        runner = CliRunner()
        result = runner.invoke(cli, ['load'])

        assert result.exit_code == 0
        assert "Successfully loaded dataset files into the database." \
            in result.output


if __name__ == "__main__":
    pytest.main()
