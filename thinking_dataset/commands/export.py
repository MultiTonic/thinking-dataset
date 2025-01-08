# @file project_root/thinking_dataset/commands/export.py
# @description Command to export processed data to the HF API dataset.
# @version 1.1.0
# @license MIT

import click
from ..utilities.log import Log
from ..utilities.logger import logger
from ..utilities.load_dotenv import dotenv
from ..utilities.exceptions import exceptions
from ..pipeworks.pipelines.pipeline import Pipeline


@click.command()
@exceptions
@logger
@dotenv(print=True)
def export(**args):
    Log.info("Starting the export command.")

    pipeline = Pipeline("export")
    pipeline.open(skip_files=True)

    Log.info("Export command completed successfully.")


if __name__ == "__main__":
    export()
