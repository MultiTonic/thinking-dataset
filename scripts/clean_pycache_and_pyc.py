import os
import shutil


def clean_pycache_and_pyc(root_dir):
    """
    Clean all __pycache__ dir and .pyc files in the given root directory.
    """
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove __pycache__ directories
        for dirname in dirnames:
            if dirname == "__pycache__":
                pycache_path = os.path.join(dirpath, dirname)
                print(f"Removing directory: {pycache_path}")
                shutil.rmtree(pycache_path)

        # Remove .pyc files
        for filename in filenames:
            if filename.endswith('.pyc'):
                pyc_path = os.path.join(dirpath, filename)
                print(f"Removing file: {pyc_path}")
                os.remove(pyc_path)


def find_duplicate_test_files(root_dir, filename):
    """
    Find duplicate test files with the same name in the given root directory.
    """
    duplicate_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        if filename in filenames:
            file_path = os.path.join(dirpath, filename)
            duplicate_files.append(file_path)

    return duplicate_files


if __name__ == "__main__":
    root_directory = "C:\\Users\\3nigma\\source\\repos\\thinking-dataset"

    # Clean __pycache__ directories and .pyc files
    clean_pycache_and_pyc(root_directory)

    # Check for duplicate test files
    duplicate_test_files = \
        find_duplicate_test_files(root_directory, "test_data_tonic.py")
    if len(duplicate_test_files) > 1:
        print("Found duplicate test files:")
        for file in duplicate_test_files:
            print(file)
    else:
        print("No duplicate test files found.")
