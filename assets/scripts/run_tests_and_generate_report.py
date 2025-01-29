"""Run tests and generate coverage reports for Thinking Dataset.

This script runs pytest, generates HTML test reports and measures
    test coverage.

Functions:
    main: Main function to run tests and generate reports.
"""

import os
import subprocess

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


def main():
    """
    Main function to run tests, generate report, and measure test coverage.
    """
    activate_venv_script = os.path.join(os.path.dirname(__file__),
                                        "activate_venv.py")

    with open(activate_venv_script) as f:
        exec(f.read(), dict(__file__=activate_venv_script))

    os.makedirs("reports", exist_ok=True)
    os.makedirs("reports/coverage", exist_ok=True)

    subprocess.run(
        [
            "pytest",
            "--html=./reports/report.html",
            "--self-contained-html",
            "--cov=thinking_dataset",
            "--cov-report=html:./reports/coverage",
        ],
        check=True,
    )

    print("HTML report and coverage report generated successfully!")


if __name__ == "__main__":
    main()
