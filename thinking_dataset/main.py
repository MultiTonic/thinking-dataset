"""
@file thinking_dataset/main.py
@description Main entry point for the Thinking Dataset Project.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import click
from thinking_dataset.commands.download import download
from thinking_dataset.commands.clean import clean


@click.group()
def cli():
    pass


cli.add_command(download)
cli.add_command(clean)

if __name__ == "__main__":
    cli()
