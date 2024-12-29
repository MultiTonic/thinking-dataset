"""
@file thinking_dataset/downloads/dataset_downloads.py
@description Provides functionalities related to dataset downloads.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
import os
from thinking_dataset.datasets.base_dataset import BaseDataset
from thinking_dataset.datasets.operations.get_download_urls \
    import GetDownloadUrls
from thinking_dataset.datasets.operations.download_file import DownloadFile

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

        console.print(f"[blue]Files to download: {', '.join(urls)}[/blue]\n")

        all_successful = True

        for file in urls:
            download_file = DownloadFile(self.connector)
            if not download_file.execute(repo_id=dataset_id,
                                         filename=file,
                                         local_dir=download_dir,
                                         token=self.token,
                                         console=console):
                all_successful = False

        if all_successful:
            console.print(
                f"[green]Successfully downloaded all {len(urls)} files "
                f"to {os.path.normpath(download_dir)}[/green]\n")
        else:
            console.print("[red]Failed to download some files. Please check "
                          "the logs for more details.[/red]\n")

        return all_successful
