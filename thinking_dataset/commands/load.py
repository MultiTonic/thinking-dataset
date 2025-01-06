# @file thinking_dataset/commands/load.py
# @description CLI command to load datasets into the database.
# @version 1.2.1
# @license MIT

import click
from ..io.files import Files
from ..utilities.log import Log
from ..db.database import Database
from ..config.config import Config
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

    config = Config.get()

    hf_read_token = kwargs['dotenv']['HF_READ_TOKEN']
    hf_write_token = kwargs['dotenv']['HF_WRITE_TOKEN']
    hf_org = kwargs['dotenv']['HF_ORG']
    hf_user = kwargs['dotenv']['HF_USER']

    data_tonic = DataTonic(read_token=hf_read_token,
                           write_token=hf_write_token,
                           org=hf_org,
                           user=hf_user,
                           config=config)
    Log.info("Initialized DataTonic instance.")

    dataset = Dataset(data_tonic=data_tonic)
    Log.info("Initialized Dataset instance.")

    files = Files(config)
    processed_path = files.get_processed_path()

    Log.info(f"Processed path: {processed_path}")

    # Log the content of the processed directory
    processed_files = files.list(processed_path)
    Log.info(f"Files in processed directory: {processed_files}")

    load_files = [
        files.get_path(processed_path, files.format(file, pattern))
        for file in config.include_files for pattern in config.load_patterns
        if file not in config.exclude_files
    ]

    Log.info(f"Parquet files to be loaded: {load_files}")

    if load_files:
        # Create the Database instance
        database = Database(config=config)

        # Check if the files exist before loading
        for load_file in load_files:
            if not Files.exists(load_file):
                Log.error(f"File not found: {load_file}")
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
