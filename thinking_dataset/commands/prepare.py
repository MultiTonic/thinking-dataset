"""
@file project_root/thinking_dataset/commands/prepare.py
@description Command to preprocess data by applying configured pipelines.
@version 1.0.0
@license MIT
"""

import click
from ..io.files import Files
from ..utilities.log import Log
from ..pipeworks.pipelines.pipeline import Pipeline
from ..utilities.command_utils import CommandUtils as Utils
from ..utilities.exceptions import exceptions
from ..utilities.logger import logger
from ..utilities.load_dotenv import dotenv


@click.command()
@click.pass_context
@exceptions
@logger
@dotenv(print=True)
def prepare(ctx, **kwargs):
    """
    Command to preprocess data by applying configured pipelines.
    """
    log = kwargs['log']
    ctx.obj = log
    Log.info(log, "Starting the prepare command.")

    config = Utils.load_dataset_config(kwargs['dotenv']['DATASET_CONFIG_PATH'])
    files = Files(config)

    raw_path = files.get_raw_path()
    processed_path = files.get_processed_path()
    files.make_dir(processed_path, log)
    Log.info(log, f"Ensured processed data directory exists: {processed_path}")

    pipelines = Pipeline.get_pipelines(config)

    for pipeline in pipelines:
        pipeline.flow(config, raw_path, processed_path, log)

    Log.info(log, "Prepare command completed successfully.")


if __name__ == "__main__":
    prepare()
