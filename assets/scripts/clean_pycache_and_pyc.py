"""Script to clean __pycache__ directories and .pyc files.

This script cleans all __pycache__ directories and .pyc files in the given
root directory. It also checks for duplicate test files.

Functions:
    clean_pycache_and_pyc: Cleans __pycache__ directories and .pyc files.
    find_duplicate_test_files: Finds duplicate test files with the same name.
    main: Main function to run the cleaning and duplicate check.
"""

import os
import shutil

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


def clean_pycache_and_pyc(path: str) -> None:
    """Cleans all __pycache__ directories and .pyc files in the given path.

    Args:
        path (str): The root directory to clean.
    """
    for parent, paths, filenames in os.walk(path):
        # Remove __pycache__ directories
        for child in paths:
            if child == "__pycache__":
                pycache = os.path.join(parent, child)
                print(f"Removing directory: {pycache}")
                shutil.rmtree(pycache)

        # Remove .pyc files
        for filename in filenames:
            if filename.endswith('.pyc'):
                pyc = os.path.join(parent, filename)
                print(f"Removing file: {pyc}")
                os.remove(pyc)


def find_duplicate_test_files(path: str, filename: str) -> list:
    """Finds duplicate test files with the same name in the given path.

    Args:
        path (str): The root directory to search for duplicate files.
        filename (str): The name of the file to search for duplicates.

    Returns:
        list: A list of paths to duplicate test files.
    """
    duplicates = []
    for dir, _, filenames in os.walk(path):
        if filename in filenames:
            file = os.path.join(dir, filename)
            duplicates.append(file)

    return duplicates


def main() -> None:
    """Main function to run the cleaning and duplicate check."""
    root_directory = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".."))

    # Clean __pycache__ directories and .pyc files
    clean_pycache_and_pyc(root_directory)

    # Check for duplicate test files
    duplicate_test_files = find_duplicate_test_files(root_directory,
                                                     "test_data_tonic.py")
    if len(duplicate_test_files) > 1:
        print("Found duplicate test files:")
        for file in duplicate_test_files:
            print(file)
    else:
        print("No duplicate test files found.")


if __name__ == "__main__":
    main()
