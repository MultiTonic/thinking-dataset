"""Script to activate the virtual environment.

This script activates the virtual environment by setting the necessary
environment variables and adding the site-packages to sys.path.

Functions:
    activate_virtualenv: Activates the virtual environment.
    main: Main function to run the activation process.
"""

import os
import sys

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


def activate_virtualenv() -> None:
    """Activates the virtual environment by setting the necessary environment
    variables and adding the site-packages to sys.path.
    """
    # Get the path to the virtual environment's Python executable
    venv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    python_executable = os.path.join(venv_path, "scripts", "python.exe")

    # Set the environment variables to activate the virtual environment
    venv_path_dir = os.path.dirname(python_executable)
    os.environ["VIRTUAL_ENV"] = venv_path
    os.environ["PATH"] = f"{venv_path_dir};{os.environ['PATH']}"

    # Add the virtual environment's site-packages to sys.path
    site_packages = os.path.join(venv_path, "Lib", "site-packages")
    sys.path.insert(0, site_packages)


def main() -> None:
    """Main function to run the activation process."""
    activate_virtualenv()


if __name__ == "__main__":
    main()
