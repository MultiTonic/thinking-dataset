"""
@file thinking_dataset/downloads/dataset_downloads.py
@description Provides functionalities related to dataset downloads.
@version 1.0.0
@license MIT
author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import os
import stat
from thinking_dataset.datasets.base_dataset import BaseDataset
from huggingface_hub import hf_hub_download

# Get the dataset type (e.g., 'parquet') from environment variables
HF_DATASET_TYPE = os.getenv("HF_DATASET_TYPE", 'parquet')


class DatasetDownloads(BaseDataset):
    """
    A class that extends BaseDataset to provide functionalities
    related to dataset downloads.

    Methods
    -------
    get_dataset_download_urls(dataset_id)
        Retrieves the download URLs for the dataset files with a
        specific type.
    download_dataset(dataset_id, download_dir, console)
        Downloads the dataset files to the specified directory.
    get_dataset_permissions(dataset_id)
        Checks the permissions of the dataset.
    get_dataset_file_list(dataset_id)
        Retrieves a list of files in the dataset.
    """

    def __init__(self, connector, token):
        super().__init__(connector)
        self.token = token

    def get_dataset_download_urls(self, dataset_id):
        """
        Retrieves the download URLs for the dataset files with a
        specific type.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to retrieve download URLs for.

        Returns
        -------
        list
            A list of download URLs for the dataset files.
        """
        dataset_info = self.get_dataset_info(dataset_id)
        download_urls = [
            file.rfilename for file in dataset_info.siblings
            if file.rfilename.endswith(f'.{HF_DATASET_TYPE}')
        ]
        self.log_info(f"Dataset download URLs: {download_urls}")
        return download_urls

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
        urls = self.get_dataset_download_urls(dataset_id)

        if not urls:
            console.print("\n[bold red]No parquet files found in the dataset."
                          "[/bold red]\n")
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
                console.print(f"[green]Downloaded {file} to "
                              f"{os.path.normpath(dest)}[/green]\n")
            except Exception as e:
                console.print(f"\n[bold red]Failed to download {file}: {e}"
                              f"[/bold red]\n")
                return False

        console.print(f"[green]Downloaded {len(urls)} parquet files to "
                      f"{os.path.normpath(download_dir)}[/green]\n")
        return True

    def get_dataset_permissions(self, dataset_id):
        """
        Checks the permissions of the dataset.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to check permissions for.

        Returns
        -------
        bool
            True if the dataset is private, False otherwise.
        """
        dataset_info = self.get_dataset_info(dataset_id)
        self.log_info(f"Dataset permissions: {dataset_info.private}")
        return dataset_info.private

    def get_dataset_file_list(self, dataset_id):
        """
        Retrieves a list of files in the dataset.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to retrieve the file list for.

        Returns
        -------
        list
            A list of files in the dataset.
        """
        dataset_info = self.get_dataset_info(dataset_id)
        file_list = dataset_info.siblings
        self.log_info(f"Dataset files: {file_list}")
        return file_list
