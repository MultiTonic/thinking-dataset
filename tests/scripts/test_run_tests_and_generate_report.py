"""
@file tests/scripts/test_run_tests_and_generate_report.py
@description Unit test for the run_tests_and_generate_report script.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import sys
import pytest
from unittest import mock
from scripts.run_tests_and_generate_report import main


def test_run_tests_and_generate_report(monkeypatch, tmp_path):
    """
    Tests the main function in the run_tests_and_generate_report script.
    """

    # Mock environment variables and os.makedirs
    monkeypatch.setenv("PATH", "")
    original_sys_path = sys.path.copy()
    original_venv = os.getenv("VIRTUAL_ENV")
    os.makedirs("reports", exist_ok=True)
    os.makedirs("reports/coverage", exist_ok=True)

    # Mock the path to the activate_venv.py script
    activate_venv_path = tmp_path / "activate_venv.py"
    with open(activate_venv_path, "w") as f:
        f.write("")

    # Mock subprocess.run
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0)

        main()

        # Check subprocess.run was called with the correct arguments
        expected_calls = [
            mock.call(
                [
                    "pytest",
                    "--html=./reports/report.html",
                    "--self-contained-html",
                    "--cov=thinking_dataset",
                    "--cov-report=html:./reports/coverage",
                ],
                check=True,
            )
        ]
        mock_run.assert_has_calls(expected_calls, any_order=True)

    # Restore the original environment variables and sys.path
    if original_venv:
        monkeypatch.setenv("VIRTUAL_ENV", original_venv)
    else:
        monkeypatch.delenv("VIRTUAL_ENV", raising=False)

    sys.path = original_sys_path


if __name__ == "__main__":
    pytest.main()
