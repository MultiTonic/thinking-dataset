"""Initialization file for the assets/scripts package.

This module imports and exposes all script modules in the package.
"""

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

from .activate_venv import activate_virtualenv
from .clean_pycache_and_pyc import (
    clean_pycache_and_pyc,
    find_duplicate_test_files,
)
from .run_llama_cpp import (
    install_llama_cpp_python,
    download_model,
)
from .run_hf_server import initialize as init_hf_server
from .generate_text import main as generate_text
from .run_cli_commands import main as run_cli_command
from .run_tests_and_generate_report import main as run_tests
from .uv.setup import main as setup_uv

__all__ = [
    'activate_virtualenv', 'clean_pycache_and_pyc',
    'find_duplicate_test_files', 'generate_text', 'run_cli_command',
    'init_hf_server', 'install_llama_cpp_python', 'download_model',
    'run_tests', 'setup_uv'
]
