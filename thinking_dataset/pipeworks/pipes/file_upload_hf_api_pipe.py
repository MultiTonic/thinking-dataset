# @file file_upload_hf_api_pipe.py
# @description Pipe to upload files to the HF API dataset based on the df.
# @version 1.0.11
# @license MIT

import os
import sys
import time
import signal
import threading
import pandas as pd

from .pipe import Pipe
from huggingface_hub import CommitInfo
from thinking_dataset.utils.log import Log
from thinking_dataset.io.files import Files
from thinking_dataset.data.data_tonic import DataTonic
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
        token = self.config.get("token", "")
        dataset = self.config.get("dataset", "")
        repo_type = self.config.get("repo_type", "")
        remote_path = self.config.get("remote_path", "")
        dry_run = self.config.get("dry_run", True)

        org = utils.parse_env_value(org)
        user = utils.parse_env_value(user)
        token = utils.parse_env_value(token)
        repo_id = utils.get_repo_id(org, dataset)

        Log.info(f"Repo Id: {repo_id} ({repo_type})")

        if not org or not dataset or not user or not repo_type:
            raise ValueError("Huggingface Organization, Dataset Name, Token, "
                             "and User are required for FileUploadHfApiPipe")

        dt = DataTonic(token, token, org, user)

        total_size = df['file_path'].map(os.path.getsize).sum()
        Log.info(
            f"Total size to upload: {text.human_readable_size(total_size)}")

        uploaded_size = 0
        abort_event = threading.Event()

        def upload_timer(file_size):
            start_time = time.time()
            while not abort_event.is_set():
                elapsed_time = time.time() - start_time
                if elapsed_time < 1:
                    time.sleep(1)
                    continue
                minutes, seconds = divmod(int(elapsed_time), 60)
                sys.stdout.write(
                    f"\rUploading file "
                    f"({file_size})... [{minutes:02}:{seconds:02}]")
                sys.stdout.flush()
                time.sleep(1)
            print("", end="")

        def upload_with_retries(file,
                                path_in_repo,
                                repo_id,
                                repo_type,
                                token,
                                retries=3):
            for attempt in range(retries):
                try:
                    return dt.api.upload_file(path_or_fileobj=file,
                                              path_in_repo=path_in_repo,
                                              repo_id=repo_id,
                                              repo_type=repo_type,
                                              token=token)
                except Exception as e:
                    if abort_event.is_set():
                        break
                    Log.error(f"Attempt {attempt + 1}/{retries} failed: {e}")
                    time.sleep(2**attempt)
            if not abort_event.is_set():
                raise RuntimeError(
                    f"Failed to upload {path_in_repo} after {retries} attempts"
                )

        def signal_handler(sig, frame):
            print("\nUpload aborted.")
            abort_event.set()
            timer_thread.join()
            sys.exit("Upload process aborted.")

        signal.signal(signal.SIGINT, signal_handler)

        for _, row in df.iterrows():
            if abort_event.is_set():
                break

            file_path = row["file_path"]
            file_name = Files.get_file_name(file_path)
            local_path = Files.get_file_path("", file_path)
            remote_file = Files.get_remote_path(remote_path, file_name)
            file_size = text.human_readable_size(os.path.getsize(local_path))
            uploaded_size += os.path.getsize(local_path)

            Log.info(f"file_path: {text.shorten_path(file_path, 80)}")
            Log.info(f"remote_path: {text.shorten_path(remote_file, 80)}")

            timer_thread = threading.Thread(target=upload_timer,
                                            args=(file_size, ))
            timer_thread.start()

            if dry_run:
                Log.info(f"Dry run: {dry_run}")
                Log.info(f"Fake upload {text.shorten_path(file_path, 80)}")
                Log.info(f"to {text.shorten_path(remote_file, 80)}")
                abort_event.set()
                timer_thread.join()
                continue

            with open(local_path, "rb") as file:
                info = upload_with_retries(file, remote_file, repo_id,
                                           repo_type, token)

                if isinstance(info, CommitInfo):
                    Log.info(
                        f"Uploaded - {text.shorten_path(remote_file, 80)}")
                    Log.info(
                        f"Uploaded {text.human_readable_size(uploaded_size)} "
                        f"of {text.human_readable_size(total_size)}")
                else:
                    raise RuntimeError(
                        "Failed to upload "
                        f"{text.shorten_path(file_path, 80)} "
                        f"to {text.shorten_path(remote_file, 80)}. "
                        f"Response: {info}")

            abort_event.set()
            timer_thread.join()

        Log.info("Completed FileUploadHfApiPipe")
        return df
