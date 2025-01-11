# @file project_root/thinking_dataset/commands/export.py
# @description Command to export processed data to the HF API dataset.
# @version 1.1.1
# @license MIT

import click
from thinking_dataset.utils.log import Log
from thinking_dataset.utils.exceptions import exceptions
from ..pipeworks.pipelines.pipeline import Pipeline


@click.command()
@exceptions
def export():
    Log.info("Starting the export command.")

    pipeline = Pipeline("export")
    pipeline.open(skip_files=True)

    Log.info("Export command completed successfully.")


if __name__ == "__main__":
    export()
