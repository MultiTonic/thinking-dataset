"""
@file thinking_dataset/commands/load.py
@description CLI command to load datasets into the database.
@version 1.0.0
@license MIT
"""

import click
from ..io.files import Files
from ..utilities.log import Log
from ..utilities.logger import logger
from ..datasets.dataset import Dataset
from ..tonics.data_tonic import DataTonic
from ..utilities.load_dotenv import dotenv
from ..utilities.exceptions import exceptions
from ..utilities.command_utils import CommandUtils as Utils


@click.command()
@click.pass_context
@exceptions
@logger
@dotenv(print=True)
def load(ctx, **kwargs):
    """
    Load downloaded datasets into local sqlite database.
    """
    log = kwargs['log']
    ctx.obj = log
    Log.info(log, "Starting the load command.")

    dataset_config_path = kwargs['dotenv']['DATASET_CONFIG_PATH']
    dataset_config = Utils.load_dataset_config(dataset_config_path)

    data_tonic = DataTonic(token=kwargs['dotenv']['HF_TOKEN'],
                           organization=kwargs['dotenv']['HF_ORGANIZATION'],
                           dataset=kwargs['dotenv']['HF_DATASET'],
                           config=dataset_config)
    Log.info(log, "Initialized DataTonic instance.")

    dataset = Dataset(data_tonic=data_tonic)
    Log.info(log, "Initialized Dataset instance.")

    files = Files(dataset_config)
    processed_data_dir = files.get_processed_path()

    load_files = [
        files.get_path(processed_data_dir, files.format(file, pattern))
        for file in dataset_config.INCLUDE_FILES
        for pattern in dataset_config.LOAD_PATTERNS
        if file not in dataset_config.EXCLUDE_FILES
    ]

    Log.info(log, f"Parquet files to be loaded: {load_files}")

    if load_files:
        database = dataset.create(
            db_url=dataset_config.DATABASE_URL.format(
                name=dataset_config.HF_DATASET),
            db_config=kwargs['dotenv']['DATABASE_CONFIG_PATH'])

        if not dataset.load(database=database, files_to_load=load_files):
            raise RuntimeError(
                "Failed to load dataset files into the database.")

        Log.info(log, "Loaded dataset files into the database successfully.")
    else:
        raise RuntimeError(
            "No files matched the filters to be loaded into the database.")


if __name__ == "__main__":
    load()
