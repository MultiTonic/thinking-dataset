# @file thinking_dataset/commands/load.py
# @description CLI command to load datasets into the database.
# @version 1.0.12
# @license MIT

import click
import os
from ..io.files import Files
from ..utilities.log import Log
from ..db.database import Database
import thinking_dataset.config as cfg
from ..utilities.logger import logger
from ..datasets.dataset import Dataset
from ..tonics.data_tonic import DataTonic
from ..utilities.load_dotenv import dotenv
from ..utilities.exceptions import exceptions


@click.command()
@exceptions
@logger
@dotenv(print=True)
def load(**kwargs):
    Log.info("Starting the load command.")

    config_instance = cfg.initialize()

    hf_read_token = config_instance.get_env_value(cfg.get_keys().HF_READ_TOKEN)
    hf_write_token = config_instance.get_env_value(
        cfg.get_keys().HF_WRITE_TOKEN)
    hf_org = config_instance.get_env_value(cfg.get_keys().HF_ORG)
    hf_user = config_instance.get_env_value(cfg.get_keys().HF_USER)

    data_tonic = DataTonic(read_token=hf_read_token,
                           write_token=hf_write_token,
                           org=hf_org,
                           user=hf_user)
    Log.info("Initialized DataTonic instance.")

    dataset = Dataset(data_tonic=data_tonic)
    Log.info("Initialized Dataset instance.")

    root_path = config_instance.get_value(cfg.get_keys().ROOT_PATH)
    process_path = config_instance.get_value(cfg.get_keys().PROCESS_PATH)
    process_dir = os.path.normpath(os.path.join(root_path, process_path))
    Files.make_dir(process_dir)
    Log.info(f"Processed path: {process_dir}")

    process_files = Files.list(process_dir)
    Log.info(f"Files in process directory: {process_files}")

    include_files = config_instance.get_value(cfg.get_keys().INCLUDE_FILES)
    load_patterns = config_instance.get_value(cfg.get_keys().LOAD_PATTERNS)
    exclude_files = config_instance.get_value(cfg.get_keys().EXCLUDE_FILES)

    load_files = []

    for file_name in include_files:
        if file_name in exclude_files:
            continue
        for pattern in load_patterns:
            load_file = os.path.normpath(pattern.format(file_name=file_name))
            full_path = os.path.join(root_path, load_file)
            if os.path.exists(full_path):
                load_files.append(full_path)
                break
            else:
                Log.error(f"File not found: {full_path}")
                raise RuntimeError(f"File not found: {full_path}")

    Log.info(f"Parquet files to be loaded: {load_files}")

    if load_files:
        database = Database()
        if not dataset.load(database=database, files_to_load=load_files):
            raise RuntimeError(
                "Failed to load dataset files into the database.")
        Log.info("Loaded dataset files into the database successfully.")
    else:
        raise RuntimeError(
            "No files matched the filters to be loaded into the database.")


if __name__ == "__main__":
    load()
