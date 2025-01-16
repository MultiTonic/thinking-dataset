# @file project_root/thinking_dataset/commands/gen.py
# @description Command to generate synthetic data.
# @version 1.0.0
# @license MIT

import click
from thinking_dataset.utils.log import Log
from thinking_dataset.utils.exceptions import exceptions
from ..pipeworks.pipelines.pipeline import Pipeline


@click.command()
@exceptions
def generate():
    Log.info("Starting the generate command.")

    pipeline = Pipeline("generate")
    pipeline.open(skip_files=True)

    Log.info("Generate command completed successfully.")


if __name__ == "__main__":
    generate()
