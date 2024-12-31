"""
@file thinking_dataset/commands/load.py
@description CLI command to load datasets into the database.
@version 1.0.0
@license MIT
"""

import sys
import click
from ..datasets.dataset import Dataset
from ..tonics.data_tonic import DataTonic
from ..config.dataset_config import DatasetConfig
from ..utilities.log import Log
from ..utilities.command_utils import CommandUtils


@click.command()
def load():
    """
    Load datasets into the database.
    """
    log = Log.setup(__package__)
    Log.info(log, "Starting the load command.")

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

        filtered_files = dataset.filter_files(dataset.list_files(),
                                              dataset.config['INCLUDE_FILES'],
                                              dataset.config['EXCLUDE_FILES'])

        if filtered_files:
            database = dataset.create(
                db_url=dataset.config['DATABASE_URL'],
                db_config=env_vars['DATABASE_CONFIG_PATH'])

            dataset.load(database=database, files_to_load=filtered_files)
            Log.info(log,
                     "Loaded dataset files into the database successfully.")
        else:
            Log.info(
                log,
                "No files matched the filters to be loaded into the database.")

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
    load()
