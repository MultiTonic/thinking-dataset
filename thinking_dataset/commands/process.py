# @file project_root/thinking_dataset/commands/prepare.py
# @description Command to preprocess data by applying configured pipelines.
# @version 1.0.2
# @license MIT

import click
from thinking_dataset.utils.log import Log
from ..pipeworks.pipelines.pipeline import Pipeline
from thinking_dataset.utils.exceptions import exceptions


@click.command()
@exceptions
def process():
    Log.info("Starting the process command.")

    pipeline = Pipeline("process")
    pipeline.open()

    Log.info("Process command completed successfully.")


if __name__ == "__main__":
    process()
