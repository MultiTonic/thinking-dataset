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
@click.pass_context
@exceptions
@logger
@dotenv(print=True)
def export(ctx, **args):
    log = args['log']
    ctx.obj = log
    Log.info(log, "Starting the export command.")

    pipeline = Pipeline(log=log, name="export")
    pipeline.open()

    Log.info(log, "Export command completed successfully.")


if __name__ == "__main__":
    export()
