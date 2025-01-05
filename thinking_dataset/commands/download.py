"""
@file thinking_dataset/commands/download.py
@description CLI command to download datasets from Hugging Face.
@version 1.0.0
@license MIT
"""

import os
import click
from ..datasets.dataset import Dataset
from ..tonics.data_tonic import DataTonic
from ..utilities.log import Log
from ..config.config import Config
from ..utilities.exceptions import exceptions
from ..utilities.logger import logger
from ..utilities.load_dotenv import dotenv
from ..io.files import Files


@click.command()
@click.pass_context
@exceptions
@logger
@dotenv(print=True)
def download(ctx, **kwargs):
    """
    Download datasets from Huggingface using Hfapi.
    """
    log = kwargs['log']
    ctx.obj = log
    Log.info(log, "Starting the download command.")

    config_path = kwargs['dotenv']['CONFIG_PATH']
    config = Config(config_path)
    config.validate()

    data_tonic = DataTonic(token=kwargs['dotenv']['HF_TOKEN'],
                           organization=kwargs['dotenv']['HF_ORGANIZATION'],
                           dataset=kwargs['dotenv']['HF_DATASET'],
                           config=config)
    Log.info(log, "Initialized DataTonic instance.")

    dataset = Dataset(data_tonic=data_tonic)
    Log.info(log, "Initialized Dataset instance.")

    files = Files(config)

    raw_dir = files.get_raw_path()
    files.make_dir(raw_dir, log)

    dataset.download(
        kwargs['dotenv']['HF_TOKEN'], f"{kwargs['dotenv']['HF_ORGANIZATION']}/"
        f"{kwargs['dotenv']['HF_DATASET']}", raw_dir,
        dataset.config['INCLUDE_FILES'], dataset.config['EXCLUDE_FILES'])
    Log.info(log,
             f"Downloaded all dataset files to {os.path.normpath(raw_dir)}")


if __name__ == "__main__":
    download()
