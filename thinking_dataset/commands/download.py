"""
@file thinking_dataset/commands/download.py
@description CLI command to download the Cablegate dataset.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
from dotenv import load_dotenv
import click
from thinking_dataset.data_tonic import DataTonic
from thinking_dataset.files import Files


@click.command()
def download():
    """
    Downloads the Cablegate dataset.
    """
    load_dotenv()  # Load environment variables from .env file

    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        click.echo("HF_TOKEN is not set. Please check your .env file.")
        return

    click.echo("Downloading Cablegate dataset...")

    files = Files()
    files.ensure_directories()

    # Initialize DataTonic client
    client = DataTonic(token=HF_TOKEN)

    # Get download URLs
    download_urls = client.downloads.get_dataset_download_urls()

    # Download files
    for url in download_urls:
        filename = url.split("/")[-1]
        dest = files.get_raw_file_path(filename)
        files.download_file(url, dest)
        click.echo(f"Downloaded {url} to {dest}")

    click.echo(f"Downloaded {len(download_urls)} files to {files.raw_dir}")


if __name__ == "__main__":
    download()
