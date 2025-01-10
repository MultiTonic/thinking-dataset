# @file thinking_dataset/main.py
# @description Main entry point for the Thinking Dataset Project.
# @version 1.2.1
# @license MIT

import click
from thinking_dataset.commands import \
    download, clean, load, prepare, export, upload
from thinking_dataset.utils.log import Log


@click.group()
def cli():
    pass


cli.add_command(download)
cli.add_command(prepare)
cli.add_command(load)
cli.add_command(clean)
cli.add_command(export)
cli.add_command(upload)

if __name__ == "__main__":
    Log.get()
    cli()
