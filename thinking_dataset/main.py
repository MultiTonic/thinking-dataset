# @file thinking_dataset/main.py
# @description Main entry point for the Thinking Dataset Project.
# @version 1.1.2
# @license MIT

import click
from thinking_dataset.commands import \
    download, clean, load, process, export, upload, ls, generate
from thinking_dataset.utils.log import Log


@click.group()
def cli():
    pass


cli.add_command(download)
cli.add_command(process)
cli.add_command(load)
cli.add_command(clean)
cli.add_command(export)
cli.add_command(upload)
cli.add_command(ls)
cli.add_command(generate)

if __name__ == "__main__":
    Log.get()
    cli()
