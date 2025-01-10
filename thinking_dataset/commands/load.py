# @file thinking_dataset/commands/load.py
# @description CLI command to load datasets into the database.
# @version 1.0.19
# @license MIT

import click
import thinking_dataset.config as conf
import thinking_dataset.config.config_keys as Keys
import thinking_dataset.dataset as td
from ..io.files import Files
from thinking_dataset.utils.log import Log
from thinking_dataset.utils.logger import logger
from ..tonics.data_tonic import DataTonic
from thinking_dataset.utils.load_dotenv import dotenv
from thinking_dataset.utils.exceptions import exceptions

CK = Keys.ConfigKeys


@click.command()
@exceptions
@logger
@dotenv(print=True)
def load(**kwargs):
    Log.info("Starting the load command.")

    conf.initialize()
    org = conf.get_env_value(CK.HF_ORG)
    user = conf.get_env_value(CK.HF_USER)
    read_token = conf.get_env_value(CK.HF_READ_TOKEN)
    write_token = conf.get_env_value(CK.HF_WRITE_TOKEN)

    dt = DataTonic(read_token=read_token,
                   write_token=write_token,
                   org=org,
                   user=user)

    Log.info("Initialized DataTonic instance.")

    dataset = td.Dataset(data_tonic=dt)

    Log.info("Initialized Dataset instance.")

    root_path = Files.get_root_path()
    process_path = Files.get_process_path()
    process_path = Files.get_file_path(root_path, process_path)
    Files.make_dir(process_path)

    Log.info(f"Processed path: {process_path}")

    files = Files.list(process_path)

    Log.info(f"Files in process directory: {files}")

    includes = conf.get_value(CK.INCLUDE_FILES)
    patterns = conf.get_value(CK.LOAD_PATTERNS)
    excludes = conf.get_value(CK.EXCLUDE_FILES)

    files = []

    for file_name in includes:
        if Files.is_excluded(file_name, excludes):
            continue
        for pattern in patterns:
            file = Files.format(file_name, pattern)
            path = Files.get_file_path(root_path, file)
            if Files.exists(path):
                files.append(path)
                break
            else:
                Log.error(f"File not found: {path}")
                raise RuntimeError(f"File not found: {path}")

    Log.info(f"Parquet files to be loaded: {files}")

    if files:
        if not dataset.load(files_to_load=files):
            raise RuntimeError(
                "Failed to load dataset files into the database.")

        Log.info("Loaded dataset files into the database successfully.")
    else:
        raise RuntimeError(
            "No files matched the filters to be loaded into the database.")


if __name__ == "__main__":
    load()
