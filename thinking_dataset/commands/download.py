# @file thinking_dataset/commands/download.py
# @description CLI command to download datasets from Hugging Face.
# @version 1.0.0
# @license MIT

import os
import click
from ..io.files import Files
from ..utilities.log import Log
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
def download(**args):
    Log.info("Starting the download command.")

    config = Config.get()

    hf_read_token = args['dotenv']['HF_READ_TOKEN']
    hf_write_token = args['dotenv']['HF_WRITE_TOKEN']
    hf_org = args['dotenv']['HF_ORG']
    hf_user = args['dotenv']['HF_USER']

    data_tonic = DataTonic(read_token=hf_read_token,
                           write_token=hf_write_token,
                           org=hf_org,
                           user=hf_user,
                           config=config)
    Log.info("Initialized DataTonic instance.")

    dataset = Dataset(data_tonic)
    Log.info("Initialized Dataset instance.")

    files = Files(config)

    raw_dir = files.get_raw_path()
    files.make_dir(raw_dir)

    dataset.download(hf_read_token, f"{hf_org}/{config.dataset_name}", raw_dir,
                     config.include_files, config.exclude_files)
    Log.info(f"Downloaded all dataset files to {os.path.normpath(raw_dir)}")


if __name__ == "__main__":
    download()
