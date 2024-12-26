"""
@file tests/scripts/test_run_tests_and_generate_report.py
@description Tests for test and generate report script
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
from scripts.run_tests_and_generate_report import main


def test_main(monkeypatch, tmp_path):
    """
    Tests the main function in the run_tests_and_generate_report script.
    """

    # Mock the environment variables and os.makedirs
    monkeypatch.setenv("PATH", "")
    original_sys_path = sys.path.copy()
    original_venv = os.getenv("VIRTUAL_ENV")
    os.makedirs("reports", exist_ok=True)

    # Mock the path to the activate_venv.py script
    activate_venv_path = tmp_path / "activate_venv.py"
    with open(activate_venv_path, "w") as f:
        f.write("")

    # Mock the subprocess.run function
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0)

        main()

        # Check that subprocess.run was called with the correct arguments
        mock_run.assert_called_with(
            [
                "pytest",
                "--cov=.",
                "--cov-report=html:reports/coverage",
                "--html=reports/report.html",
                "--self-contained-html",
            ],
            check=True,
        )

    # Restore the original environment variables and sys.path
    if original_venv:
        monkeypatch.setenv("VIRTUAL_ENV", original_venv)
    else:
        monkeypatch.delenv("VIRTUAL_ENV", raising=False)

    sys.path = original_sys_path


if __name__ == "__main__":
    pytest.main()
