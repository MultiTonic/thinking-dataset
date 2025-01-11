# @file project_root/thinking_dataset/commands/prepare.py
# @description Command to preprocess data by applying configured pipelines.
# @version 1.0.1
# @license MIT

import click
from thinking_dataset.utils.log import Log
from ..pipeworks.pipelines.pipeline import Pipeline
from thinking_dataset.utils.exceptions import exceptions


@click.command()
@exceptions
def prepare():
    Log.info("Starting the prepare command.")

    pipeline = Pipeline("prepare")
    pipeline.open()

    Log.info("Prepare command completed successfully.")


if __name__ == "__main__":
    prepare()
