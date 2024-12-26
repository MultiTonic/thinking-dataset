"""
@file thinking_dataset/tests/commands/test_clean.py
@description Tests for the clean command in the Thinking Dataset Project.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from dotenv import load_dotenv
from click.testing import CliRunner
from thinking_dataset.main import cli


# Load environment variables from .env file
load_dotenv()


def test_clean_function(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(cli, ['clean'])

    assert result.exit_code == 0
    assert "Removed directory" in result.output or \
           "No directory found" in result.output
    assert "Created clean directory" in result.output


if __name__ == "__main__":
    pytest.main()
