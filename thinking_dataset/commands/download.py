"""
@file thinking_dataset/commands/download.py
@description CLI command to download all parquet files in the Cablegate
dataset using Hugging Face CLI.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import stat
from dotenv import load_dotenv
from rich.console import Console
import click
from huggingface_hub import hf_hub_download, HfFolder
from thinking_dataset.io.files import Files
from thinking_dataset.tonics.data_tonic import DataTonic


def load_env_variables():
    load_dotenv()
    env_vars = {
        "HF_TOKEN": os.getenv("HF_TOKEN"),
        "HF_DATASET": os.getenv("HF_DATASET"),
        "HF_ORGANIZATION": os.getenv("HF_ORGANIZATION"),
        "ROOT_DIR": os.path.abspath(os.getenv("ROOT_DIR", ".")),
        "DATA_DIR": os.getenv("DATA_DIR", "data"),
        "HF_HOME":
        os.path.expanduser(os.getenv("HF_HOME", "~/.cache/huggingface"))
    }
    print("Loaded environment variables:", env_vars)
    return env_vars


def set_hf_cache_dir(cache_dir):
    os.environ['HF_HOME'] = cache_dir
    HfFolder.path = cache_dir
    print("Set Hugging Face cache directory:", cache_dir)


def construct_paths(root_dir, data_dir):
    base_dir = os.path.join(root_dir, data_dir)
    raw_dir = os.path.join(base_dir, "raw")
    processed_dir = os.path.join(base_dir, "processed")

    print(f"Constructed paths - Base Dir: {base_dir}, Raw Dir: {raw_dir}, "
          f"Processed Dir: {processed_dir}")
    return raw_dir, processed_dir


def validate_env_variables(env_vars, console):
    if not all(env_vars.values()):
        console.print(
            "\n[bold red]HF_TOKEN, HF_DATASET, or HF_ORGANIZATION is not set. "
            "Please check your .env file.[/bold red]\n")
        return False
    return True


def download_files(env_vars, raw_dir, console):
    console.print(f"\n[green]Using HF_TOKEN: {env_vars['HF_TOKEN']}[/green]")
    console.print("[green]Downloading all parquet files in "
                  "the Cablegate dataset...[/green]\n")

    files = Files(raw_dir=raw_dir, processed_dir=None)
    files.ensure_directories()

    # Use DataTonic for downloading files
    datatonic = DataTonic(token=env_vars['HF_TOKEN'])
    dataset_id = f"{env_vars['HF_ORGANIZATION']}/{env_vars['HF_DATASET']}"
    urls = datatonic.downloads.get_dataset_download_urls(dataset_id)

    if not urls:
        console.print(
            "\n[bold red]No parquet files found in the dataset.[/bold red]\n")
        return

    for file in urls:
        dest = files.get_file_path(raw_dir, file)
        console.print(f"[green]Downloading {file} to {dest}...[/green]")
        if os.path.exists(dest):
            try:
                os.chmod(dest, stat.S_IWRITE)
                os.remove(dest)
            except PermissionError as e:
                console.print(f"\n[bold red]PermissionError: {e}[/bold red]\n")
        try:
            hf_hub_download(repo_id=dataset_id,
                            filename=file,
                            local_dir=raw_dir,
                            token=env_vars['HF_TOKEN'],
                            repo_type="dataset")
            console.print("[green]Downloaded " + file + " to " +
                          f"{os.path.normpath(dest)}[/green]\n")
        except Exception as e:
            console.print(
                f"\n[bold red]Failed to download {file}: {e}[/bold red]\n")

    console.print("[green]Downloaded " + str(len(urls)) +
                  " parquet files to " +
                  f"{os.path.normpath(raw_dir)}[/green]\n")


@click.command()
def download():
    """
    Download all parquet files the Cablegate dataset using Hugging Face CLI.
    """
    console = Console()

    # Load environment variables
    env_vars = load_env_variables()

    # Set Hugging Face cache directory
    set_hf_cache_dir(env_vars['HF_HOME'])

    # Validate environment variables
    if not validate_env_variables(env_vars, console):
        return

    # Construct paths
    raw_dir, processed_dir = construct_paths(env_vars['ROOT_DIR'],
                                             env_vars['DATA_DIR'])

    # Download files
    download_files(env_vars, raw_dir, console)


if __name__ == "__main__":
    download()
