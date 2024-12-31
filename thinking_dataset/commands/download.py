"""
@file thinking_dataset/commands/download.py
@description CLI command to download datasets from Hugging Face.
@version 1.0.0
@license MIT
"""

import os
import sys
import click
from ..datasets.dataset import Dataset
from ..tonics.data_tonic import DataTonic
from ..utilities.log import Log as Log
from ..config.dataset_config import DatasetConfig
from ..utilities.command_utils import CommandUtils


@click.command()
def download():
    """
    Download datasets from Hugging Face.
    """
    log = Log.setup(__name__)
    Log.info(log, "Starting the download command.")

    try:
        env_vars = CommandUtils.load_env_variables(log)
        CommandUtils.print_env_config(env_vars, log)

        if not CommandUtils.validate_env_variables(env_vars, log):
            raise ValueError("Failed to validate environment variables.")

        dataset_config_path = env_vars['DATASET_CONFIG_PATH']
        dataset_config = DatasetConfig(dataset_config_path)
        dataset_config.validate()

        data_tonic = DataTonic(token=env_vars['HF_TOKEN'],
                               organization=env_vars['HF_ORGANIZATION'],
                               dataset=env_vars['HF_DATASET'],
                               config=dataset_config)
        Log.info(log, "Initialized DataTonic instance.")

        dataset = Dataset(data_tonic=data_tonic)
        Log.info(log, "Initialized Dataset instance.")

        raw_dir = CommandUtils.get_raw_data_path(log, env_vars['ROOT_DIR'],
                                                 env_vars['DATA_DIR'],
                                                 dataset_config.RAW_DIR)

        dataset.download(
            env_vars['HF_TOKEN'],
            f"{env_vars['HF_ORGANIZATION']}/{env_vars['HF_DATASET']}", raw_dir,
            dataset.config['INCLUDE_FILES'], dataset.config['EXCLUDE_FILES'])
        Log.info(
            log,
            f"Downloaded all dataset files to {os.path.normpath(raw_dir)}")

    except ValueError as e:
        Log.error(log, f"Validation error: {e}", exc_info=True)
        sys.exit(1)
    except FileNotFoundError as e:
        Log.error(log, f"File not found error: {e}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        Log.error(log, f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    download()
