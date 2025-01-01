"""
@file project_root/thinking_dataset/commands/preprocess.py
@description Command to preprocess data by applying configured pipelines.
@version 1.0.0
@license MIT
"""

import os
import sys
import click
from ..utilities.log import Log
from ..pipeworks.pipelines.pipeline import Pipeline
from ..utilities.command_utils import CommandUtils as Utils


@click.command()
def preprocess():
    """
    Command to preprocess data by applying configured pipelines.
    """
    log = Log.setup(__name__)
    Log.info(log, "Starting the preprocess command.")
    error_occurred = False

    try:
        env_vars = Utils.load_env_variables(log)
        Utils.print_env_config(env_vars, log)

        if not Utils.validate_env_variables(env_vars, log):
            raise ValueError("Failed to validate environment variables.")

        dataset_config = Utils.load_dataset_config(
            env_vars['DATASET_CONFIG_PATH'])
        raw_data_dir = Utils.get_raw_data_path(log, dataset_config.ROOT_DIR,
                                               dataset_config.DATA_DIR,
                                               dataset_config.RAW_DIR)

        pipelines = Pipeline.setup(dataset_config, log)

        for file in dataset_config.INCLUDE_FILES:
            if file in dataset_config.EXCLUDE_FILES:
                Log.info(log, f"Skipping excluded file: {file}")
                continue

            input_file = os.path.join(raw_data_dir, file)
            output_file = os.path.join(raw_data_dir, f"processed_{file}")

            df = Utils.load_data(input_file, dataset_config.DATASET_TYPE)

            for pipeline in pipelines:
                df = pipeline.flow(df, log)

            Utils.save_data(df, output_file, dataset_config.DATASET_TYPE)

            Log.info(log, f"Data preprocessed and saved to {output_file}")

    except ValueError as e:
        Log.error(log, f"Validation error: {e}", exc_info=True)
        error_occurred = True
    except FileNotFoundError as e:
        Log.error(log, f"File not found error: {e}", exc_info=True)
        error_occurred = True
    except Exception as e:
        Log.error(log, f"An unexpected error occurred: {e}", exc_info=True)
        error_occurred = True
    finally:
        if error_occurred:
            sys.exit(1)
        else:
            Log.info(log, "Preprocess command completed successfully.")


if __name__ == "__main__":
    preprocess()
