"""
@file thinking_dataset/datasets/operations/get_download_file.py
@description Operation to download a specific file from the dataset.
@version 1.0.0
@license MIT
"""
import os
import stat
from .base_operation import Operation
from huggingface_hub import hf_hub_download
from ...utilities.log import Log


class GetDownloadFile(Operation):
    """
    A class to download a specific file from the dataset.
    """

    def execute(self, repo_id: str, filename: str, local_dir: str, token: str):
        """
        Downloads a file from the specified dataset repository and saves it
        to the given path.
        """
        dest = os.path.join(local_dir, filename)
        normalized_dest = os.path.normpath(dest)

        Log.info(f"Downloading {filename} to {normalized_dest}...")

        if os.path.exists(dest):
            try:
                os.chmod(dest, stat.S_IWRITE)
                os.remove(dest)
            except PermissionError as e:
                self.log.error(f"PermissionError: {e}")
                return False

        try:
            hf_hub_download(repo_id=repo_id,
                            filename=filename,
                            local_dir=local_dir,
                            token=token,
                            repo_type="dataset")
            return True
        except Exception as e:
            self.log.error(f"Failed to download {filename}: {e}",
                           exc_info=True)
            return False
