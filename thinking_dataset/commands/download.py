# @file thinking_dataset/commands/download.py
# @description Command to download datasets.
# @version 1.0.4
# @license MIT

import click
from thinking_dataset.utils.log import Log
from thinking_dataset.utils.exceptions import exceptions
from thinking_dataset.utils.logger import logger
from thinking_dataset.utils.load_dotenv import dotenv
import thinking_dataset.config as config
from ..tonics.data_tonic import DataTonic
from ..datasets.dataset import Dataset


@click.command()
@exceptions
@logger
@dotenv(print=True)
def download(**kwargs):
    Log.info("Starting the download command.")

    config_instance = config.initialize()

    dt = DataTonic(read_token=config_instance.get_env_value(
        config.get_keys().HF_READ_TOKEN),
                   write_token=config_instance.get_env_value(
                       config.get_keys().HF_WRITE_TOKEN),
                   org=config_instance.get_value(config.get_keys().HF_ORG),
                   user=config_instance.get_env_value(
                       config.get_keys().HF_USER))
    Log.info("Initialized DataTonic instance.")

    dataset = Dataset(data_tonic=dt)
    Log.info("Initialized Dataset instance.")

    success = dataset.download()

    if success:
        Log.info(
            "Downloaded dataset "
            f"{config_instance.get_value(config.get_keys().DATASET_NAME)} "
            "successfully.")
    else:
        Log.error(
            "Failed to download dataset: "
            f"{config_instance.get_value(config.get_keys().DATASET_NAME)}")

    Log.info("Download command completed successfully.")


if __name__ == "__main__":
    download()
