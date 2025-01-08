# @file thinking_dataset/commands/load.py
# @description CLI command to load datasets into the database.
# @version 1.0.3
# @license MIT

import click
from ..io.files import Files
from ..utilities.log import Log
from ..db.database import Database
from ..config.config import Config
from ..config.config_keys import ConfigKeys as Keys
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

    hf_read_token = Config.get_env_value(Keys.HF_READ_TOKEN)
    hf_write_token = Config.get_env_value(Keys.HF_WRITE_TOKEN)
    hf_org = Config.get_env_value(Keys.HF_ORG)
    hf_user = Config.get_env_value(Keys.HF_USER)

    data_tonic = DataTonic(read_token=hf_read_token,
                           write_token=hf_write_token,
                           org=hf_org,
                           user=hf_user)
    Log.info("Initialized DataTonic instance.")

    dataset = Dataset(data_tonic=data_tonic)
    Log.info("Initialized Dataset instance.")

    process_path = Files.get_process_path()

    Log.info(f"Processed path: {process_path}")

    process_files = Files.list(process_path)
    Log.info(f"Files in process directory: {process_files}")

    load_files = [
        Files.get_file_path(process_path, Files.format(file, pattern))
        for file in Config.get_value(Keys.INCLUDE_FILES)
        for pattern in Config.get_value(Keys.LOAD_PATTERNS)
        if file not in Config.get_value(Keys.EXCLUDE_FILES)
    ]

    Log.info(f"Parquet files to be loaded: {load_files}")

    if load_files:
        database = Database()
        for load_file in load_files:
            if not Files.exists(load_file):
                raise RuntimeError(f"File not found: {load_file}")

        if not dataset.load(database=database, files_to_load=load_files):
            raise RuntimeError(
                "Failed to load dataset files into the database.")

        Log.info("Loaded dataset files into the database successfully.")
    else:
        raise RuntimeError(
            "No files matched the filters to be loaded into the database.")


if __name__ == "__main__":
    load()
