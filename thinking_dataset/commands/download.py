"""
@file thinking_dataset/commands/download.py
@description CLI command to download all parquet files in the Cablegate
dataset using Hugging Face CLI.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import stat
from dotenv import load_dotenv
from rich.console import Console
import click
from huggingface_hub import HfApi, hf_hub_download
from thinking_dataset.io.files import Files


@click.command()
def download():
    """
    Downloads all parquet files in the Cablegate dataset using Hugging Face
    CLI.
    """
    console = Console()

    load_dotenv()

    HF_TOKEN = os.getenv("HF_TOKEN")
    HF_DATASET = os.getenv("HF_DATASET")
    HF_ORGANIZATION = os.getenv("HF_ORGANIZATION")
    ROOT_DIR = os.getenv("ROOT_DIR", "/")
    DATA_DIR = os.getenv("DATA_DIR", "data")

    # Define the directory names
    RAW_DIR_NAME = "raw"
    PROCESSED_DIR_NAME = "processed"
    CABLEGATE_DIR_NAME = "cablegate"

    # Construct the directory paths
    base_dir = os.path.join(ROOT_DIR, DATA_DIR)
    raw_dir = os.path.join(base_dir, RAW_DIR_NAME, CABLEGATE_DIR_NAME)
    processed_dir = os.path.join(base_dir, PROCESSED_DIR_NAME,
                                 CABLEGATE_DIR_NAME)

    if not HF_TOKEN or not HF_DATASET or not HF_ORGANIZATION:
        console.print("\n[bold red]HF_TOKEN, HF_DATASET, or HF_ORGANIZATION"
                      " is not set. Please check your .env file.[/bold red]\n")
        return

    console.print(f"\n[green]Using HF_TOKEN: {HF_TOKEN}[/green]")
    console.print("[green]Downloading all parquet files in the Cablegate"
                  " dataset...[/green]\n")

    files = Files()
    files.ensure_directories([raw_dir, processed_dir])

    api = HfApi()
    dataset_id = f"{HF_ORGANIZATION}/{HF_DATASET}"

    try:
        # List all files in the repository
        repo_files = api.list_repo_files(repo_id=dataset_id, token=HF_TOKEN,
                                         repo_type="dataset")
        console.print(f"[green]Found {len(repo_files)} files in the dataset."
                      f"[/green]")
        # Filter for parquet files
        parquet_files = [file for file in repo_files if file.endswith(
            '.parquet')]
    except Exception as e:
        console.print(
            f"\n[bold red]Error fetching dataset files: {e}[/bold red]\n")
        return

    if not parquet_files:
        console.print("\n[bold red]No parquet files found in the dataset."
                      "[/bold red]\n")
        return

    for file in parquet_files:
        dest = files.get_file_path(raw_dir, file)
        console.print(f"[green]Downloading {file}...[/green]")
        if os.path.exists(dest):
            try:
                os.chmod(dest, stat.S_IWRITE)
                os.remove(dest)
            except PermissionError as e:
                console.print(f"\n[bold red]PermissionError: {e}[/bold red]\n")
        try:
            hf_hub_download(repo_id=dataset_id, filename=file,
                            local_dir=raw_dir, token=HF_TOKEN,
                            repo_type="dataset")
            console.print(f"[green]Downloaded {file} to {dest}[/green]\n")
        except Exception as e:
            console.print(
                f"\n[bold red]Failed to download {file}: {e}[/bold red]\n")

    console.print(f"[green]Downloaded {len(parquet_files)} parquet files to "
                  f"{raw_dir}[/green]\n")


if __name__ == "__main__":
    download()
