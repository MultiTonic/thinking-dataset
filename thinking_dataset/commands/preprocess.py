"""
@file project_root/thinking_dataset/commands/preprocess.py
@description Command to preprocess data by applying configured pipelines.
@version 1.0.0
@license MIT
"""

import os
import sys
import click
from ..io.files import Files
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
        env_vars = Utils.load_env_vars(log)
        Utils.print_env_vars(env_vars, log)

        if not Utils.validate_env_vars(env_vars, log):
            raise ValueError("Failed to validate environment variables.")

        dataset_config = Utils.load_dataset_config(
            env_vars['DATASET_CONFIG_PATH'])
        files = Files(dataset_config)

        raw_data_dir = files.get_raw_path()
        files.make_dir(raw_data_dir)
        Log.info(log, f"Ensured raw data directory exists: {raw_data_dir}")

        pipelines = Pipeline.setup(dataset_config, log)

        for file in dataset_config.INCLUDE_FILES:
            if Files.is_excluded(file, dataset_config.EXCLUDE_FILES, log):
                continue

            input_file = Files.get_path(raw_data_dir, file)
            Log.info(log, f"Processing file: {input_file}")

            if not os.path.exists(input_file):
                Log.error(log, f"File not found: {input_file}")
                error_occurred = True
                continue

            output_file = Files.get_path(raw_data_dir, f"processed_{file}")

            df = Utils.read_data(input_file, dataset_config.DATASET_TYPE)

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
            Log.error(log, "Preprocess command did not complete.")
            sys.exit(1)
        else:
            Log.info(log, "Preprocess command completed successfully.")


if __name__ == "__main__":
    preprocess()
