# @file thinking_dataset/commands/clean.py
# @description Command to clean the data directory and other dynamic resources.
# @version 1.0.0
# @license MIT

import os
import click
from ..utilities.log import Log
from ..utilities.command_utils import CommandUtils as Utils
from ..utilities.exceptions import exceptions
from ..utilities.logger import logger
from ..utilities.load_dotenv import dotenv
from ..io.files import Files


@click.command()
@click.pass_context
@exceptions
@logger
@dotenv(print=True)
def clean(ctx, **kwargs):
    """
    Cleans the data directory and other dynamic resources.
    """
    log = kwargs['log']
    ctx.obj = log
    Log.info(log, "Starting the clean command.")

    config_path = kwargs['dotenv']['CONFIG_PATH']
    config = Utils.load_config(config_path)

    files = Files(config)
    path = files.get_path(config.root_path, config.data_path)

    if not os.path.exists(path):
        Log.info(log, f"Directory not found: {path}")
        Log.info(log, "Clean command completed with no changes.")
        return

    removed_files_count = 0
    removed_dirs_count = 0
    skipped_count = 0

    def onerror(func, path, exc_info):
        nonlocal skipped_count
        Log.warn(log, f"Skipping {path} due to {exc_info[1]}")
        skipped_count += 1

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
        Log.warn(
            log, f"Skipping file {e.filename} "
            "as it is being used by another process.")
        skipped_count += 1

    total_removed = removed_files_count + removed_dirs_count
    summary = f"Cleanup Summary: {total_removed} items removed"
    if skipped_count > 0:
        summary += f" ({skipped_count} items skipped)"

    Log.info(log, summary)
    Log.info(log, "Clean command completed successfully.")


if __name__ == "__main__":
    clean()
