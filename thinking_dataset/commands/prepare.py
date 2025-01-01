"""
@file project_root/thinking_dataset/commands/prepare.py
@description Command to preprocess data by applying configured pipelines.
@version 1.0.0
@license MIT
"""

import os
import click
from ..io.files import Files
from ..utilities.log import Log
from ..pipeworks.pipelines.pipeline import Pipeline
from ..utilities.command_utils import CommandUtils as Utils
from ..utilities.handle_exceptions import handle_exceptions


@click.command()
@click.pass_context
@handle_exceptions
def prepare(ctx):
    """
    Command to preprocess data by applying configured pipelines.
    """
    log = Log.setup(__name__)
    ctx.obj = log
    Log.info(log, "Starting the prepare command.")

    env_vars = Utils.load_env_vars(log)
    Utils.print_env_vars(env_vars, log)

    if not Utils.validate_env_vars(env_vars, log):
        raise ValueError("Failed to validate environment variables.")

    config = Utils.load_dataset_config(env_vars['DATASET_CONFIG_PATH'])
    files = Files(config)

    raw_path = files.get_raw_path()
    processed_path = files.get_processed_path()
    files.make_dir(processed_path)
    Log.info(log, f"Ensured processed data directory exists: {processed_path}")

    pipelines = Pipeline.setup(config, log)

    for pipeline in pipelines:
        prepare_file = pipeline.config.get("prepare_file")

        for file in config.INCLUDE_FILES:
            if Files.is_excluded(file, config.EXCLUDE_FILES, log):
                continue

            input_file = Files.get_path(raw_path, file)
            Log.info(log, f"Processing file: {input_file}")

            if not Files.exists(input_file):
                raise FileNotFoundError(f"File not found: {input_file}")

            file_root, file_ext = os.path.splitext(file)
            file_name = prepare_file.format(file_base=file_root,
                                            file_ext=file_ext)
            file_path = Files.get_path(processed_path, file_name)

            df = Utils.read_data(input_file, config.DATASET_TYPE)

            for pipe in pipeline.pipes:
                df = pipe.flow(df, log)

            Utils.save_data(df, file_path, config.DATASET_TYPE)

            Log.info(log, f"Data processed and saved to {file_path}")


if __name__ == "__main__":
    prepare()
