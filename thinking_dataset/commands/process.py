# @file project_root/thinking_dataset/commands/prepare.py
# @description Command to preprocess data by applying configured pipelines.
# @version 1.0.0
# @license MIT

import click
from thinking_dataset.utils.log import Log
from ..pipeworks.pipelines.pipeline import Pipeline
from thinking_dataset.utils.exceptions import exceptions
from thinking_dataset.utils.logger import logger
from thinking_dataset.utils.load_dotenv import dotenv


@click.command()
@exceptions
@logger
@dotenv(print=True)
def process(**kwargs):
    Log.info("Starting the process command.")

    pipeline = Pipeline("process")
    pipeline.open()

    Log.info("Process command completed successfully.")


if __name__ == "__main__":
    process()
