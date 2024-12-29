"""
@file thinking_dataset/tonics/data_tonic.py
@description DataTonic class for managing dataset operations.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
import os
from huggingface_hub.utils import RepositoryNotFoundError
from thinking_dataset.connectors.connector import Connector
from thinking_dataset.datasets.operations.get_download_urls import (
    GetDownloadUrls, )
from thinking_dataset.datasets.operations.get_download_file \
    import GetDownloadFile
from thinking_dataset.datasets.operations.dataset_operations import (
    DatasetOperations, )

HF_ORGANIZATION = os.getenv("HF_ORGANIZATION")
HF_DATASET = os.getenv("HF_DATASET")


class DataTonic(Connector):
    """
    A class that extends Connector to manage dataset operations for a
    specified organization and dataset.

    Attributes
    ----------
    organization : str
        The organization to which the datasets belong.
    dataset : str
        The specific dataset to manage.
    HF_DATASET_TYPE : str
        The dataset type (e.g., 'parquet') for file extensions.
    operations : DatasetOperations
        An instance of the DatasetOperations class for dataset operations.
    get_download_urls : GetDownloadUrls
        An instance of the GetDownloadUrls class for retrieving download URLs.
    get_download_file : GetDownloadFile
        An instance of the GetDownloadFile class for downloading files.

    Methods
    -------
    get_dataset_info(dataset_id)
        Retrieves dataset information for the given dataset ID.
    """

    def __init__(self,
                 token,
                 organization=HF_ORGANIZATION,
                 dataset=HF_DATASET):
        """
        Constructs all the necessary attributes for the DataTonic object.

        Parameters
        ----------
        token : str
            The API token for authentication.
        organization : str, optional
            The organization of datasets belong to (default is HF_ORGANIZATION)
        dataset : str, optional
            The specific dataset to manage (default is HF_DATASET).
        """
        super().__init__(token)
        self.organization = organization
        self.dataset = dataset
        self.HF_DATASET_TYPE = os.getenv("HF_DATASET_TYPE", "parquet")
        self.operations = DatasetOperations(self)
        self.get_download_urls = GetDownloadUrls(self)
        self.get_download_file = GetDownloadFile(self)

    def get_dataset_info(self, dataset_id):
        try:
            return self.api.dataset_info(dataset_id)
        except RepositoryNotFoundError as e:
            print(f"Error retrieving dataset info for {dataset_id}: {e}")
            raise

    def download_dataset(self, dataset_id, token, download_dir, console):
        urls = self.get_download_urls.execute(dataset_id)
        if not urls:
            console.print("\n[bold red]No parquet files found "
                          "in the dataset.[/bold red]\n")
            return False

        console.print(f"[blue]Files to download: {', '.join(urls)}[/blue]\n")

        all_successful = True
        for file in urls:
            if not self.get_download_file.execute(
                    repo_id=dataset_id,
                    filename=file,
                    local_dir=download_dir,
                    token=token,
                    console=console,
            ):
                all_successful = False

        if all_successful:
            console.print("[green]Successfully downloaded all files to "
                          f"{os.path.normpath(download_dir)}[/green]\n")
        else:
            console.print("[red]Failed to download some files. "
                          "Please check the logs for more details.[/red]\n")

        return all_successful
