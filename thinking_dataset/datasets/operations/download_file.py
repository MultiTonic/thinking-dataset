"""
@file thinking_dataset/datasets/operations/download_file.py
@description Operation to download a specific file from the dataset.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""
import os
import stat
from .base_operation import BaseOperation
from huggingface_hub import hf_hub_download


class DownloadFile(BaseOperation):
    """
    A class to download a specific file from the dataset.
    """

    def execute(self, repo_id: str, filename: str, local_dir: str, token: str,
                console):
        """
        Downloads a file from the specified dataset repository and saves it
        to the given path.

        Parameters
        ----------
        repo_id : str
            The ID of the dataset repository.
        filename : str
            The name of the file to download.
        local_dir : str
            The local directory to save the downloaded file.
        token : str
            The token for authentication.
        console : rich.console.Console
            The console for printing progress.

        Returns
        -------
        bool
            True if the file was downloaded successfully, False otherwise.
        """
        dest = os.path.join(local_dir, filename)
        console.print(f"[green]Downloading {filename} to {dest}...[/green]")
        if os.path.exists(dest):
            try:
                os.chmod(dest, stat.S_IWRITE)
                os.remove(dest)
            except PermissionError as e:
                console.print(f"\n[bold red]PermissionError: {e}[/bold red]\n")
                return False
        try:
            hf_hub_download(repo_id=repo_id,
                            filename=filename,
                            local_dir=local_dir,
                            token=token,
                            repo_type="dataset")
            console.print(f"[green]Downloaded {filename} "
                          f"to {os.path.normpath(dest)}[/green]\n")
            self.log_info(f"File downloaded successfully to {dest}")
            return True
        except Exception as e:
            console.print(
                f"\n[bold red]Failed to download {filename}: {e}[/bold red]\n")
            return False
