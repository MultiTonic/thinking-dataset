# @file thinking_dataset/dataset/operations/download_operation.py
# @description Implementation of the DownloadOperation class.
# @version 1.0.2
# @license MIT

from thinking_dataset.dataset.dataset_keys import DatasetKeys as DK
from thinking_dataset.utils.log import Log
from thinking_dataset.io.files import Files


class DownloadOperation:
    """
    A class for handling dataset downloads.
    """

    def __init__(self, api, attributes):
        self.api = api
        self.attributes = attributes

    def execute(self) -> bool:
        try:
            token = self.attributes[DK.READ_TOKEN]
            repo_id = f"{self.attributes[DK.ORG]}/{self.attributes[DK.NAME]}"
            dataset_info = self.api.get_info.execute(repo_id)
            if dataset_info:
                Log.info(f"Downloading dataset {repo_id}...")

                download_urls = self.api.get_download_urls.execute(repo_id)
                filtered_urls = self.filter_files(download_urls,
                                                  self.attributes[DK.INCLUDE],
                                                  self.attributes[DK.EXCLUDE])

                path = Files.get_raw_path()
                for url in filtered_urls:
                    self.api.get_download_file.execute(repo_id, url, path,
                                                       token)

                Log.info(f"Dataset {repo_id} downloaded successfully.")
                return True
            else:
                raise ValueError(f"Dataset {repo_id} not found.")
        except Exception as e:
            raise RuntimeError(f"Error downloading dataset: {e}")

    def filter_files(self, all_files: list, include_files: list,
                     exclude_files: list) -> list:
        if include_files:
            all_files = [file for file in all_files if file in include_files]
        if exclude_files:
            all_files = [
                file for file in all_files if file not in exclude_files
            ]
        return all_files
