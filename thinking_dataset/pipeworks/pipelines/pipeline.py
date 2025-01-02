"""
@file thinking_dataset/pipeworks/pipelines/pipeline.py
@description Defines the Pipeline class for managing data processing pipelines.
@version 1.0.0
@license MIT
"""

import os
from typing import List
from ..pipes.pipe import Pipe
from ...utilities.command_utils import CommandUtils as Utils
from ...utilities.log import Log
from ...io.files import Files
from ...utilities.text_utils import TextUtils as Text


class Pipeline:

    def __init__(self, pipes: List[Pipe], config: dict):
        self.pipes = pipes
        self.config = config

    def flow(self, config, raw_path, processed_path, log):
        prepare_file = self.config.get("prepare_file")

        for file in config.INCLUDE_FILES:
            if Files.is_excluded(file, config.EXCLUDE_FILES, log):
                continue

            input_file = Files.get_path(raw_path, file)
            Log.info(log, f"Processing file: {input_file}")

            if not Files.exists(input_file):
                Log.warn(log, f"File not found: {input_file}")
                continue

            file_root, file_ext = os.path.splitext(file)
            file_name = prepare_file.format(file_base=file_root,
                                            file_ext=file_ext)
            file_path = Files.get_path(processed_path, file_name)

            df = Utils.read_data(input_file, config.DATASET_TYPE)

            for pipe in self.pipes:
                Log.info(log, f"Running {pipe.__class__.__name__} on {file}")
                df = pipe.flow(df, log)

            Utils.to(df, file_path, config.DATASET_TYPE)

            file_size = os.path.getsize(file_path)
            human_readable_file_size = Text.human_readable_size(file_size)
            Log.info(
                log, f"Data processed and saved to {file_path} "
                f"(Size: {human_readable_file_size})")

    @staticmethod
    def get_pipelines(dataset_config):
        """
        Set up the pipeline based on the dataset configuration.
        """
        pipeline_configs = dataset_config.PIPELINES
        pipelines = []
        for pipeline_config in pipeline_configs:
            pipes = []
            for pipe_config in pipeline_config['pipeline']['pipes']:
                details = pipe_config['pipe']
                type = details['type']
                pipe = Pipe.get_pipe(type)
                pipes.append(pipe(details['config']))

            pipeline = Pipeline(pipes, pipeline_config['pipeline']['config'])
            pipelines.append(pipeline)

        return pipelines
