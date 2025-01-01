"""
@file thinking_dataset/commands/clean.py
@description Command to clean the data directory and other dynamic resources.
@version 1.0.0
@license MIT
"""

import os
import shutil
import click
from ..utilities.log import Log
from ..utilities.command_utils import CommandUtils
from ..utilities.handle_exceptions import handle_exceptions
from ..io.files import Files


@click.command()
@click.pass_context
@handle_exceptions
def clean(ctx):
    """
    Cleans the data directory and other dynamic resources.
    """
    log = Log.setup(__name__)
    ctx.obj = log
    Log.info(log, "Starting the clean command.")

    env_vars = CommandUtils.load_env_vars(log)
    CommandUtils.print_env_vars(env_vars, log)

    if not CommandUtils.validate_env_vars(env_vars, log):
        raise ValueError("Failed to validate environment variables.")

    dataset_config_path = env_vars['DATASET_CONFIG_PATH']
    dataset_config = CommandUtils.load_dataset_config(dataset_config_path)

    files = Files(dataset_config)
    base_dir_path = os.path.abspath(
        files.get_path(dataset_config.ROOT_DIR, dataset_config.DATA_DIR))

    if files.exists(base_dir_path):
        shutil.rmtree(base_dir_path)
        Log.info(log, f"Removed directory: {base_dir_path}")
    else:
        Log.info(log, f"No directory found at {base_dir_path}")

    files.make_dir(base_dir_path)
    Log.info(log, f"Created clean directory: {base_dir_path}")


if __name__ == "__main__":
    clean()
