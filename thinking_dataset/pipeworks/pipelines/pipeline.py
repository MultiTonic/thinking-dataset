"""
@file project_root/thinking_dataset/pipeworks/pipelines/pipeline.py
@description Defines the Pipeline class for managing data processing pipelines.
@version 1.0.0
@license MIT
"""

from typing import List
from ..pipes.pipe import Pipe
from ...utilities.command_utils import CommandUtils


class Pipeline:

    def __init__(self, pipes: List[Pipe]):
        self.pipes = pipes

    def flow(self, df, log):
        for pipe in self.pipes:
            df = pipe.flow(df, log)
        return df

    @staticmethod
    def setup(dataset_config, log):
        """
        Set up the pipeline based on the dataset configuration.
        """

        pipeline_configs = dataset_config.PIPELINES
        pipelines = []
        for pipeline_config in pipeline_configs:
            pipes = []
            for pipe_config in pipeline_config['pipeline']['pipes']:
                pipe_details = pipe_config['pipe']
                pipe_type = pipe_details['type']
                pipe_class = CommandUtils.get_pipe_class(pipe_type, log)
                pipes.append(Pipe(pipe_class, pipe_details['config']))

            pipeline = Pipeline(pipes)
            pipelines.append(pipeline)

        return pipelines
