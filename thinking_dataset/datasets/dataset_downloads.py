"""
@file thinking_dataset/downloads/dataset_downloads.py
@description Provides functionalities related to dataset downloads.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
import os
import stat
from thinking_dataset.datasets.base_dataset import BaseDataset
from huggingface_hub import hf_hub_download
from thinking_dataset.datasets.operations.get_download_urls \
    import GetDownloadUrls

# Get the dataset type (e.g., 'parquet') from environment variables
HF_DATASET_TYPE = os.getenv("HF_DATASET_TYPE", 'parquet')


class DatasetDownloads(BaseDataset):
    """
    A class that extends BaseDataset to provide functionalities
    related to dataset downloads.

    Methods
    -------
    download_dataset(dataset_id, download_dir, console)
        Downloads the dataset files to the specified directory.
    """

    def __init__(self, connector, token):
        super().__init__(connector)
        self.connector = connector  # Ensure connector is initialized
        self.token = token

    def download_dataset(self, dataset_id, download_dir, console):
        """
        Downloads the dataset files to the specified directory.

        Parameters
        ----------
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
        get_download_urls = GetDownloadUrls(self.connector)
        urls = get_download_urls.execute(dataset_id)

        if not urls:
            console.print("\n[bold red]No parquet files found in "
                          "the dataset.[/bold red]\n")
            return False

        for file in urls:
            dest = os.path.join(download_dir, file)
            console.print(f"[green]Downloading {file} to {dest}...[/green]")
            if os.path.exists(dest):
                try:
                    os.chmod(dest, stat.S_IWRITE)
                    os.remove(dest)
                except PermissionError as e:
                    console.print(
                        f"\n[bold red]PermissionError: {e}[/bold red]\n")
                    return False
            try:
                hf_hub_download(repo_id=dataset_id,
                                filename=file,
                                local_dir=download_dir,
                                token=self.token,
                                repo_type="dataset")
                console.print(f"[green]Downloaded {file} "
                              f"to {os.path.normpath(dest)}[/green]\n")
            except Exception as e:
                console.print(
                    f"\n[bold red]Failed to download {file}: {e}[/bold red]\n")
                return False

        console.print(f"[green]Downloaded {len(urls)} parquet files "
                      f"to {os.path.normpath(download_dir)}[/green]\n")
        return True
