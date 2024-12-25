"""
@file Scripts/activate_venv.py
@description Script to activate the virtual environment.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import sys


def activate_virtualenv():
    """
    Activates the virtual environment by setting the necessary environment
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


if __name__ == "__main__":
    activate_virtualenv()
