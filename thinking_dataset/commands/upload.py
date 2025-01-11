# @file thinking_dataset/commands/upload.py
# @description Command to upload processed data to the HF API dataset.
# @version 1.0.2
# @license MIT

import click
from ..utils.log import Log
from ..utils.exceptions import exceptions
from ..pipeworks.pipelines.pipeline import Pipeline


@click.command()
@exceptions
def upload():
    Log.info("Starting the upload command.")

    pipeline = Pipeline("upload")
    pipeline.open(skip_files=True)

    Log.info("Upload command completed successfully.")


if __name__ == "__main__":
    upload()
