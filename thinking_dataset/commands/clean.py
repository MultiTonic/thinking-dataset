"""
@file thinking_dataset/commands/clean.py
@description Command to clean the data directory and other dynamic resources.
@version 1.0.0
@license MIT
"""

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

    config_path = kwargs['dotenv']['DATASET_CONFIG_PATH']
    config = Utils.load_dataset_config(config_path)

    files = Files(config)
    path = files.get_path(config.ROOT_DIR, config.DATA_DIR)

    try:
        Files.remove_dir(path, log)
    except PermissionError as e:
        Log.warning(
            log, f"Skipping file {e.filename} as it is "
            "being used by another process.")

    Log.info(log, "Clean command completed successfully.")


if __name__ == "__main__":
    clean()
