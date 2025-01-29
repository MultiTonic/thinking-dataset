"""Pipeline Management Module.

This module provides functionality for managing data processing pipelines,
handling pipeline configuration, execution, and monitoring.

Functions:
    None

Classes:
    Pipeline: Manages pipeline execution and configuration.
"""

import os
import time
import pandas as pd
import thinking_dataset.config as conf
from ...io.files import Files
from ..pipes.pipe import Pipe
from thinking_dataset.utils.log import Log
from thinking_dataset.utils.command_utils import CommandUtils as utils

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


class Pipeline:
    """Pipeline orchestration and execution manager.

    This class manages:
    1. Pipeline configuration and setup
    2. Data flow through processing pipelines
    3. File I/O operations and path management
    4. Execution monitoring and logging

    Attributes:
        pipelines (list): List of registered pipeline configurations
        config (Config): Global configuration instance
        in_path (str): Input data path
        out_path (str): Output data path
        name (str): Pipeline identifier
    """

    pipelines = []

    def __init__(self, name=None):
        """Initialize pipeline manager.

        Args:
            name (str, optional): Pipeline identifier. Defaults to None.
        """
        self.config = conf.initialize()
        self.in_path, self.out_path = self._setup_paths()
        self.name = name
        self._setup_pipelines()

    def get(self, name):
        """Get pipeline configuration by name.

        Args:
            name (str): Name of pipeline to retrieve

        Returns:
            tuple: (pipes, config) for named pipeline

        Raises:
            ValueError: If pipeline name not found
        """
        for pname, pipes, pconfig in Pipeline.pipelines:
            if pname == name:
                return pipes, pconfig
        raise ValueError(f"Pipeline '{name}' not found")

    def get_batch_size(self, pipeline_config: dict) -> int:
        """Get batch size from pipeline configuration.

        Args:
            pipeline_config (dict): Pipeline configuration dictionary

        Returns:
            int: Configured batch size or default value of 1
        """
        return pipeline_config.get('batch_size', 1)

    def open(self, skip_files=False):
        """Execute pipeline processing.

        Args:
            skip_files (bool, optional): Whether to skip file operations.
                Defaults to False.
        """
        start_time = time.time()
        pipes, config = self.get(self.name)
        self._open(pipes, skip_files=skip_files)
        end_time = time.time()
        elapsed_time = end_time - start_time
        human_readable_time = time.strftime("%H:%M:%S",
                                            time.gmtime(elapsed_time))
        Log.info(f"Total running time: {human_readable_time}")

    def _setup_paths(self):
        """Set up input and output paths."""
        config = conf.Config.get()
        self.out_path = config.get_value(conf.get_keys().PROCESS_PATH)
        Files.make_dir(self.out_path)
        return config.get_value(conf.get_keys().RAW_PATH), self.out_path

    def _setup_pipelines(self):
        """Configure pipeline instances from config."""
        configs = self.config.pipelines
        pipes = []
        for pconfig in configs:
            name = pconfig['pipeline']['name']
            if name == self.name:
                for pipe in pconfig['pipeline']['pipes']:
                    type = pipe['pipe']['type']
                    inst = Pipe.get_pipe(type)
                    pipes.append(inst(pipe['pipe'].get('config', {})))
                Pipeline.pipelines.append(
                    (name, pipes, pconfig['pipeline']['config']))
                break

    def _process_pipes(self, df, pipes, skip_files=False):
        """Process DataFrame through sequence of pipes."""
        _, config = self.get(self.name)
        for pipe in pipes:
            Log.info(f"Open -- {pipe.__class__.__name__}")
            df = pipe.flow(df, pipeline_config=config)
        return df

    def _save_data(self, df: pd.DataFrame, file_path: str) -> None:
        """Save DataFrame to file with proper error handling.

        Args:
            df (pd.DataFrame): DataFrame to save
            file_path (str): Path to save the file

        Raises:
            RuntimeError: If save operation fails
        """
        try:
            Log.info(f"Saving data to: {file_path}")
            utils.to(df, file_path, self.config.dataset_type)
            Log.info("Data saved successfully")
        except Exception as e:
            Log.error(f"Failed to save data: {str(e)}")
            raise RuntimeError(f"Failed to save data: {str(e)}") from e

    def _process_file(self, file, pipes, skip_files=False):
        """Process a single file through the pipeline."""
        try:
            input_file = Files.get_file_path(self.in_path, file)
            Log.info(f"Processing file: {input_file}")

            if not skip_files:
                if not Files.exists(input_file):
                    raise FileNotFoundError(f"File not found: {input_file}")

            df = utils.read_data(input_file, self.config.dataset_type)
            df = self._process_pipes(df, pipes, skip_files)

            if not skip_files:
                base_name, ext = os.path.splitext(file)
                file_name = f"{base_name}{ext}"
                file_path = Files.get_file_path(self.out_path, file_name)
                self._save_data(df, file_path)

            return df
        except Exception as e:
            Log.error(f"Pipeline processing failed: {str(e)}")
            raise RuntimeError("Pipeline processing failed") from e

    def _open(self, pipes, skip_files=False):
        """Open and process pipeline sequence."""
        try:
            files = self.config.include_files or []
            for file in files:
                if not Files.is_excluded(file, self.config.exclude_files):
                    self._process_file(file, pipes, skip_files)
        except Exception as e:
            Log.error(f"Pipeline execution failed: {str(e)}")
            raise RuntimeError("Pipeline execution failed") from e
