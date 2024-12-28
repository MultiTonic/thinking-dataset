"""
@file thinking_dataset/tests/test_main_function.py
@description High-level tests for the main function in the Thinking Dataset.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from click.testing import CliRunner
from thinking_dataset.main import cli

# Load environment variables from .env file
load_dotenv()


def test_main_function(monkeypatch):
    with patch('thinking_dataset.commands.download.DataTonic',
               new=MagicMock()):
        runner = CliRunner()
        result = runner.invoke(cli, ['download'])

        assert result.exit_code == 0
        assert "Loaded environment variables" in result.output
        assert "Set Hugging Face cache directory" in result.output
        assert "Constructed paths" in result.output
        assert "Downloaded all dataset files" in result.output


def test_clean_function(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(cli, ['clean'])

    assert result.exit_code == 0
    assert "Removed directory" in result.output or \
           "No directory found" in result.output
    assert "Created clean directory" in result.output


if __name__ == "__main__":
    pytest.main()
