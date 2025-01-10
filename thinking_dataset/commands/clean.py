# @file thinking_dataset/commands/clean.py
# @description Command to clean the data directory and other dynamic resources.
# @version 1.0.3
# @license MIT

import os
import click
from thinking_dataset.utils.log import Log
from thinking_dataset.utils.exceptions import exceptions
from thinking_dataset.utils.logger import logger
from thinking_dataset.utils.load_dotenv import dotenv
from ..io.files import Files
import thinking_dataset.config as conf


@click.command()
@exceptions
@logger
@dotenv(print=True)
def clean(**kwargs):
    Log.info("Starting the clean command.")

    config = conf.initialize()
    path = Files.get_file_path(config.paths['root'], config.paths['data'])

    if not Files.exists(path):
        Log.info(f"Directory not found: {path}")
        Log.info("Clean command completed with no changes.")
        return

    removed_files_count, removed_dirs_count, skipped_count = _clean_directory(
        path)

    summary = _generate_summary(removed_files_count, removed_dirs_count,
                                skipped_count)
    Log.info(summary)
    Log.info("Clean command completed successfully.")


def _clean_directory(path):
    removed_files_count = 0
    removed_dirs_count = 0
    skipped_count = 0

    def count_removals(path):
        nonlocal removed_files_count, removed_dirs_count
        if Files.exists(path):
            if os.path.isdir(path):
                if not Files.list(path):
                    removed_dirs_count += 1
            else:
                removed_files_count += 1

    try:
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                file_path = Files.get_file_path(root, name)
                count_removals(file_path)
                Files.remove_file(file_path)
            for name in dirs:
                dir_path = Files.get_file_path(root, name)
                count_removals(dir_path)
                Files.remove_dir(dir_path)
        Files.remove_dir(path)
    except PermissionError as e:
        Log.warn(f"Skipping file {e.filename} as it is "
                 "being used by another process.")
        skipped_count += 1

    return removed_files_count, removed_dirs_count, skipped_count


def _generate_summary(removed_files_count, removed_dirs_count, skipped_count):
    total_removed = removed_files_count + removed_dirs_count
    summary = f"Cleanup Summary: {total_removed} items removed"
    if skipped_count > 0:
        summary += f" ({skipped_count} items skipped)"
    return summary


if __name__ == "__main__":
    clean()
