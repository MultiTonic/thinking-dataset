# @file thinking_dataset/commands/clean.py
# @description Command to clean the data directory and other dynamic resources.
# @version 1.0.0
# @license MIT

import os
import click
from ..utilities.log import Log
from ..utilities.exceptions import exceptions
from ..utilities.logger import logger
from ..utilities.load_dotenv import dotenv
from ..io.files import Files
from ..config.config import Config


@click.command()
@exceptions
@logger
@dotenv(print=True)
def clean(**kwargs):
    Log.info("Starting the clean command.")

    config = Config.get()
    files = Files(config)
    path = files.get_path(config.root_path, config.data_path)

    if not os.path.exists(path):
        Log.info(f"Directory not found: {path}")
        Log.info("Clean command completed with no changes.")
        return

    removed_files_count = 0
    removed_dirs_count = 0
    skipped_count = 0

    def count_removals(path):
        nonlocal removed_files_count, removed_dirs_count
        if os.path.isfile(path):
            removed_files_count += 1
        elif os.path.isdir(path):
            removed_dirs_count += 1

    try:
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                count_removals(file_path)
                os.remove(file_path)
            for name in dirs:
                dir_path = os.path.join(root, name)
                count_removals(dir_path)
                os.rmdir(dir_path)
        os.rmdir(path)
    except PermissionError as e:
        Log.warn(f"Skipping file {e.filename} "
                 "as it is being used by another process.")
        skipped_count += 1

    total_removed = removed_files_count + removed_dirs_count
    summary = f"Cleanup Summary: {total_removed} items removed"
    if skipped_count > 0:
        summary += f" ({skipped_count} items skipped)"

    Log.info(summary)
    Log.info("Clean command completed successfully.")


if __name__ == "__main__":
    clean()
