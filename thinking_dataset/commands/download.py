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
@click.pass_context
@exceptions
@logger
@dotenv(print=True)
def download(ctx, **args):
    log = args['log']
    ctx.obj = log
    Log.info(log, "Starting the download command.")

    path = args['dotenv']['CONFIG_PATH']
    config = Config(path)
    config.validate()

    hf_token = args['dotenv']['HF_TOKEN']
    hf_org = args['dotenv']['HF_ORG']
    hf_user = args['dotenv']['HF_USER']

    data_tonic = DataTonic(token=hf_token,
                           org=hf_org,
                           user=hf_user,
                           dataset=config.dataset_name,
                           config=config)
    Log.info(log, "Initialized DataTonic instance.")

    dataset = Dataset(data_tonic=data_tonic)
    Log.info(log, "Initialized Dataset instance.")

    files = Files(config)

    raw_dir = files.get_raw_path()
    files.make_dir(raw_dir, log)

    dataset.download(hf_token, f"{hf_org}/{config.dataset_name}", raw_dir,
                     config.include_files, config.exclude_files)
    Log.info(log,
             f"Downloaded all dataset files to {os.path.normpath(raw_dir)}")


if __name__ == "__main__":
    download()
