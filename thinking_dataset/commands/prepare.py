# @file project_root/thinking_dataset/commands/prepare.py
# @description Command to preprocess data by applying configured pipelines.
# @version 1.0.0
# @license MIT

import click
from ..utilities.log import Log
from ..pipeworks.pipelines.pipeline import Pipeline
from ..utilities.exceptions import exceptions
from ..utilities.logger import logger
from ..utilities.load_dotenv import dotenv


@click.command()
@exceptions
@logger
@dotenv(print=True)
def prepare(**kwargs):
    Log.info("Starting the prepare command.")

    pipeline = Pipeline("prepare")
    pipeline.open()

    Log.info("Prepare command completed successfully.")


if __name__ == "__main__":
    prepare()
