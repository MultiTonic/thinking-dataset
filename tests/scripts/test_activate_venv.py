"""
@file tests/scripts/test_activate_venv.py
@description Tests for activate_venv script in the Thinking Dataset Project.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import sys
import pytest
from unittest import mock
from scripts.activate_venv import activate_virtualenv


def test_activate_virtualenv(monkeypatch, tmp_path):
    """
    Tests the activate_virtualenv function.
    """

    # Mock the environment variables and sys.path
    monkeypatch.setenv("PATH", "")
    original_sys_path = sys.path.copy()
    original_venv = os.getenv("VIRTUAL_ENV")

    # Mock the path to the virtual environment
    venv_path = tmp_path / "venv"
    os.makedirs(venv_path / "scripts")
    python_executable = venv_path / "scripts" / "python.exe"

    # Create a mock os.path.abspath function
    with mock.patch("os.path.abspath") as mock_abspath:
        mock_abspath.return_value = str(venv_path)

        activate_virtualenv()

        # Check the environment variables
        assert os.getenv("VIRTUAL_ENV") == str(venv_path)
        assert os.path.dirname(str(python_executable)) in os.getenv("PATH")

        # Check the site-packages directory in sys.path
        site_packages = os.path.join(str(venv_path), "Lib", "site-packages")
        assert site_packages in sys.path

    # Restore the original environment variables and sys.path
    if original_venv:
        monkeypatch.setenv("VIRTUAL_ENV", original_venv)
    else:
        monkeypatch.delenv("VIRTUAL_ENV", raising=False)

    sys.path = original_sys_path


if __name__ == "__main__":
    pytest.main()
