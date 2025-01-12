# @file thinking_dataset/pipeworks/pipes/file_upload_hf_api_pipe.py
# @desc Uploads files to the HF API dataset based on the DataFrame.
# @version 1.0.31
# @license MIT

import pandas as pd
from .pipe import Pipe
from huggingface_hub import CommitInfo
from thinking_dataset.utils.log import Log
from thinking_dataset.io.files import Files
from thinking_dataset.tonics.data_tonic import DataTonic
from thinking_dataset.utils.text_utils import TextUtils as text
from thinking_dataset.utils.command_utils import CommandUtils as utils


class FileUploadHfApiPipe(Pipe):
    """
    Pipe to upload files to the HF API dataset based on the DataFrame.
    """

    def flow(self, df: pd.DataFrame, **args) -> pd.DataFrame:
        Log.info("Starting FileUploadHfApiPipe")

        org = self.config.get("org", "")
        user = self.config.get("user", "")
        dataset = self.config.get("dataset", "")
        token = self.config.get("token", "")
        repo_type = self.config.get("repo_type", "")
        remote_path = self.config.get("remote_path", "")
        dry_run = self.config.get("dry_run", True)

        org = utils.parse_env_value(org)
        user = utils.parse_env_value(user)
        token = utils.parse_env_value(token)
        repo_id = utils.get_repo_id(org, dataset)

        Log.info(f"User: {user}")
        Log.info(f"Repo Id: {repo_id}")
        Log.info(f"Repo Type: {repo_type}")

        if not org or not dataset or not user or not repo_type:
            raise ValueError("Huggingface Organization, Dataset Name, Token, "
                             "and User are required for FileUploadHfApiPipe")

        dt = DataTonic(token, token, org, user)

        for _, row in df.iterrows():
            file_path = row["file_path"]
            file_name = Files.get_file_name(file_path)
            local_path = Files.get_file_path("", file_path)
            remote_path = Files.get_remote_path(remote_path, file_name)

            Log.info(f"file_path: {text.shorten_path(file_path, 80)}")
            Log.info(f"remote_path: {text.shorten_path(remote_path, 80)}")

            if dry_run:
                Log.info(f"Dry run: {dry_run}")
                Log.info(f"Fake upload {text.shorten_path(file_path, 80)}")
                Log.info(f"to {text.shorten_path(remote_path, 80)}")
                return df

            with open(local_path, "rb") as file:
                info = dt.api.upload_file(path_or_fileobj=file,
                                          path_in_repo=remote_path,
                                          repo_id=repo_id,
                                          repo_type=repo_type,
                                          token=token)

                if isinstance(info, CommitInfo):
                    Log.info("Successfully uploaded")
                else:
                    raise RuntimeError(
                        "Failed to upload "
                        f"{text.shorten_path(file_path, 80)} "
                        f"to {text.shorten_path(remote_path, 80)}. "
                        f"Response: {info}")
        return df
