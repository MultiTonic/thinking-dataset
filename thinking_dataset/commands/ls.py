# @file thinking_dataset/commands/ls.py
# @description Command to list all files in the DataTonic dataset directory.
# @version 1.0.13
# @license MIT

import click
import sys
import thinking_dataset.config as conf
import thinking_dataset.config.config_keys as Keys
import thinking_dataset.dataset as Dataset

from thinking_dataset.utils.log import Log
from thinking_dataset.utils.logger import logger
from thinking_dataset.utils.load_dotenv import dotenv
from thinking_dataset.utils.exceptions import exceptions
from thinking_dataset.tonics.data_tonic import DataTonic

CK = Keys.ConfigKeys
D = Dataset.Dataset
DT = DataTonic


@click.command()
@exceptions
@logger
@dotenv(print=True)
def ls():
    try:
        conf.initialize()
        org = conf.get_env_value(CK.HF_ORG)
        user = conf.get_env_value(CK.HF_USER)
        read_token = conf.get_env_value(CK.HF_READ_TOKEN)
        write_token = conf.get_env_value(CK.HF_WRITE_TOKEN)

        dt = DT(read_token=read_token,
                write_token=write_token,
                org=org,
                user=user)

        d = D(dt)
        files = d.get_file_list()

        if not files:
            click.echo("No files found.")
            return

        click.echo("Files in the dataset:")
        for file in files:
            click.echo(f"- {file.name}")

    except Exception as e:
        Log.error(f"Error listing files: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    ls()
