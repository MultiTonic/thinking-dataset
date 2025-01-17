"""
@file scripts/run_tests_and_generate_report.py
@description Script to run tests, generate report, and measure test coverage.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import subprocess


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
