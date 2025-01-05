# @file thinking_dataset/commands/load.py
# @description CLI command to load datasets into the database.
# @version 1.0.0
# @license MIT

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
    log = kwargs['log']
    ctx.obj = log
    Log.info(log, "Starting the load command.")

    config_path = kwargs['dotenv']['CONFIG_PATH']
    config = Utils.load_config(config_path)

    hf_token = kwargs['dotenv']['HF_TOKEN']
    hf_org = kwargs['dotenv']['HF_ORG']
    hf_user = kwargs['dotenv']['HF_USER']

    data_tonic = DataTonic(token=hf_token,
                           org=hf_org,
                           user=hf_user,
                           dataset=config.dataset_name,
                           config=config)
    Log.info(log, "Initialized DataTonic instance.")

    dataset = Dataset(data_tonic=data_tonic)
    Log.info(log, "Initialized Dataset instance.")

    files = Files(config)
    processed_path = files.get_processed_path()

    load_files = [
        files.get_path(processed_path, files.format(file, pattern))
        for file in config.include_files for pattern in config.load_patterns
        if file not in config.exclude_files
    ]

    Log.info(log, f"Parquet files to be loaded: {load_files}")

    if load_files:
        database = dataset.create(
            db_url=config.database_url.format(name=config.dataset_name),
            config=kwargs['dotenv']['CONFIG_PATH'])

        if not dataset.load(database=database, files_to_load=load_files):
            raise RuntimeError(
                "Failed to load dataset files into the database.")

        Log.info(log, "Loaded dataset files into the database successfully.")
    else:
        raise RuntimeError(
            "No files matched the filters to be loaded into the database.")


if __name__ == "__main__":
    load()
