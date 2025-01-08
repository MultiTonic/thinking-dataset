# @file thinking_dataset/commands/download.py
# @description Command to download datasets.
# @version 1.0.1
# @license MIT

import click
from ..utilities.log import Log
from ..utilities.exceptions import exceptions
from ..utilities.logger import logger
from ..utilities.load_dotenv import dotenv
from ..config.config import Config
from ..config.config_keys import ConfigKeys as Keys
from ..tonics.data_tonic import DataTonic
from ..datasets.dataset import Dataset


@click.command()
@exceptions
@logger
@dotenv(print=True)
def download(**kwargs):
    Log.info("Starting the download command.")

    dt = DataTonic(read_token=Config.get_env_value(Keys.HF_READ_TOKEN),
                   write_token=Config.get_env_value(Keys.HF_WRITE_TOKEN),
                   org=Config.get_value(Keys.HF_ORG),
                   user=Config.get_env_value(Keys.HF_USER))
    Log.info("Initialized DataTonic instance.")

    dataset = Dataset(data_tonic=dt)
    Log.info("Initialized Dataset instance.")

    success = dataset.download()

    if success:
        Log.info("Downloaded dataset "
                 f"{Config.get_value(Keys.DATASET_NAME)} successfully.")
    else:
        Log.error("Failed to download dataset: "
                  f"{Config.get_value(Keys.DATASET_NAME)}")

    Log.info("Download command completed successfully.")


if __name__ == "__main__":
    download()
