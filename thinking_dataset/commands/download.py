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
from dotenv import load_dotenv
from rich.console import Console
import click
from thinking_dataset.tonics.data_tonic import DataTonic
from thinking_dataset.datasets.operations.get_download_urls \
    import GetDownloadUrls
from thinking_dataset.datasets.operations.get_download_file \
    import GetDownloadFile


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
    print("Set Hugging Face cache directory:", cache_dir)


def construct_paths(root_dir, data_dir):
    base_dir = os.path.join(root_dir, data_dir)
    raw_dir = os.path.join(base_dir, "raw")
    processed_dir = os.path.join(base_dir, "processed")

    print("Constructed paths - "
          f"Base Dir: {base_dir}, "
          f"Raw Dir: {raw_dir}, "
          f"Processed Dir: {processed_dir}")
    return raw_dir, processed_dir


def validate_env_variables(env_vars, console):
    if not all(env_vars.values()):
        console.print(
            "\n[bold red]HF_TOKEN, HF_DATASET, or HF_ORGANIZATION is not set. "
            "Please check your .env file.[/bold red]\n")
        return False
    return True


def download_dataset(connector, token, dataset_id, download_dir,
                     console: Console):
    """
    Downloads the dataset files to the specified directory.

    Parameters
    ----------
    connector : DataTonic
        The connector object for accessing the dataset.
    token : str
        The authentication token.
    dataset_id : str
        The ID of the dataset to download files for.
    download_dir : str
        The directory to download the files to.
    console : rich.console.Console
        The console for printing progress.

    Returns
    -------
    bool
        True if all files were downloaded successfully, False otherwise.
    """
    get_download_urls = GetDownloadUrls(connector)
    urls = get_download_urls.execute(dataset_id)

    if not urls:
        console.print(
            "\n[bold red]No parquet files found in the dataset.[/bold red]\n")
        return False

    console.print(f"[blue]Files to download: {', '.join(urls)}[/blue]\n")

    all_successful = True

    for file in urls:
        download_file = GetDownloadFile(connector)
        if not download_file. \
            execute(repo_id=dataset_id,
                    filename=file,
                    local_dir=download_dir,
                    token=token,
                    console=console):
            all_successful = False

    if all_successful:
        console.print("[green]Successfully downloaded "
                      f"all {len(urls)} files "
                      f"to {os.path.normpath(download_dir)}[/green]\n")
    else:
        console.print("[red]Failed to download some files. "
                      "Please check the logs for more details.[/red]\n")

    return all_successful


@click.command()
def download():
    """
    Download all parquet files in the Cablegate dataset using Hugging Face CLI.
    """
    console = Console()

    env_vars = load_env_variables()

    set_hf_cache_dir(env_vars['HF_HOME'])

    if not validate_env_variables(env_vars, console):
        return

    raw_dir, processed_dir = construct_paths(env_vars['ROOT_DIR'],
                                             env_vars['DATA_DIR'])

    datatonic = DataTonic(token=env_vars['HF_TOKEN'])
    dataset_id = f"{env_vars['HF_ORGANIZATION']}/{env_vars['HF_DATASET']}"

    if not download_dataset(datatonic, env_vars['HF_TOKEN'], dataset_id,
                            raw_dir, console):
        console.print(
            "\n[bold red]Failed to download dataset files.[/bold red]\n")
    else:
        console.print(f"[green]Downloaded all dataset"
                      f"files to {os.path.normpath(raw_dir)}[/green]\n")


if __name__ == "__main__":
    download()
