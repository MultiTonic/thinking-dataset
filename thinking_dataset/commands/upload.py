# @file thinking_dataset/commands/upload.py
# @description Command to upload processed data to the HF API dataset.
# @version 1.0.1
# @license MIT

import click
from ..utils.log import Log
from ..utils.logger import logger
from ..utils.load_dotenv import dotenv
from ..utils.exceptions import exceptions
from ..pipeworks.pipelines.pipeline import Pipeline


@click.command()
@exceptions
@logger
@dotenv(print=True)
def upload(**args):
    Log.info("Starting the upload command.")

    pipeline = Pipeline("upload")
    pipeline.open(skip_files=True)

    Log.info("Upload command completed successfully.")


if __name__ == "__main__":
    upload()