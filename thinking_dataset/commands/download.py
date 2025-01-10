# @file thinking_dataset/commands/download.py
# @description Command to download datasets.
# @version 1.0.9
# @license MIT

import click
import thinking_dataset.config as conf
import thinking_dataset.config.config_keys as Keys
import thinking_dataset.dataset as td
from ..tonics.data_tonic import DataTonic
from thinking_dataset.utils.log import Log
from thinking_dataset.utils.logger import logger
from thinking_dataset.utils.load_dotenv import dotenv
from thinking_dataset.utils.exceptions import exceptions

CK = Keys.ConfigKeys


@click.command()
@exceptions
@logger
@dotenv(print=True)
def download():
    Log.info("Starting the download command.")

    conf.initialize()
    dt = DataTonic(read_token=conf.get_env_value(CK.HF_READ_TOKEN),
                   write_token=conf.get_env_value(CK.HF_WRITE_TOKEN),
                   org=conf.get_value(CK.HF_ORG),
                   user=conf.get_env_value(CK.HF_USER))

    Log.info("Initialized DataTonic instance.")

    d = td.Dataset(data_tonic=dt)

    Log.info("Initialized Dataset instance.")

    completed = d.download()
    if completed:
        Log.info("Downloaded dataset "
                 f"{conf.get_value(CK.DATASET_NAME)} "
                 "successfully.")
    else:
        Log.error("Failed to download dataset: "
                  f"{conf.get_value(CK.DATASET_NAME)}")

    Log.info("Download command completed successfully.")


if __name__ == "__main__":
    download()
