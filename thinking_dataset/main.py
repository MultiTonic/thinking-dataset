"""
@file thinking_dataset/main.py
@description Main entry point for the Thinking Dataset Project.
@version 1.0.0
@license MIT
"""

import click
from thinking_dataset.commands.download import download
from thinking_dataset.commands.clean import clean
from thinking_dataset.commands.load import load
from thinking_dataset.commands.prepare import prepare


@click.group()
def cli():
    pass


cli.add_command(download)
cli.add_command(prepare)
cli.add_command(load)
cli.add_command(clean)

if __name__ == "__main__":
    cli()
