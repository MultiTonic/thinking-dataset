# @file project_root/thinking_dataset/commands/prepare.py
# @description Command to preprocess data by applying configured pipelines.
# @version 1.0.0
# @license MIT

import click
from thinking_dataset.utils.log import Log
from thinking_dataset.utils.logger import logger
from ..pipeworks.pipelines.pipeline import Pipeline
from thinking_dataset.utils.load_dotenv import dotenv
from thinking_dataset.utils.exceptions import exceptions


@click.command()
@exceptions
@logger
@dotenv(print=True)
def prepare():
    Log.info("Starting the prepare command.")

    pipeline = Pipeline("prepare")
    pipeline.open()

    Log.info("Prepare command completed successfully.")


if __name__ == "__main__":
    prepare()
