"""Pipeline Management Module.

This module provides functionality for managing and executing data processing
pipelines, handling configuration, file I/O, and pipeline orchestration.

Functions:
    None

Classes:
    Pipeline: Manages pipeline configuration, execution and monitoring.
"""

import os
import time

import pandas as pd

from thinking_dataset.config import initialize, Config, get_keys
from thinking_dataset.io.files import Files
from thinking_dataset.pipeworks.pipes.pipe import Pipe
from thinking_dataset.utils.command_utils import CommandUtils as utils
from thinking_dataset.utils.log import Log

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
        self.config = initialize()
        self.in_path, self.out_path = self._setup_paths()
        self.name = name
        self._setup_pipelines()

    @classmethod
    def register_pipeline(cls, name: str, pipes: list, config: dict) -> None:
        """Register a new pipeline configuration.

        Args:
            name (str): Pipeline identifier
            pipes (list): List of pipe instances
            config (dict): Pipeline configuration
        """
        cls.pipelines.append((name, pipes, config))

    @classmethod
    def get(cls, name: str) -> tuple:
        """Get pipeline configuration by name.

        Args:
            name (str): Name of pipeline to retrieve

        Returns:
            tuple: (pipes, config) for named pipeline

        Raises:
            ValueError: If pipeline name not found
        """
        for pname, pipes, pconfig in cls.pipelines:
            if pname == name:
                return pipes, pconfig
        raise ValueError(f"Pipeline '{name}' not found")

    @staticmethod
    def get_batch_size(pipeline_config: dict) -> int:
        """Get batch size from pipeline configuration.

        Args:
            pipeline_config (dict): Pipeline configuration dictionary

        Returns:
            int: Configured batch size or default value of 1
        """
        return pipeline_config.get('batch_size', 1)

    @property
    def elapsed_time(self) -> float:
        """Get elapsed execution time in seconds.

        Returns:
            float: Elapsed time between start and end
        """
        if hasattr(self, 'start_time') and hasattr(self, 'end_time'):
            return self.end_time - self.start_time
        return 0.0

    @property
    def elapsed_time_human(self) -> str:
        """Get human readable elapsed time.

        Returns:
            str: Formatted time string (HH:MM:SS)
        """
        return time.strftime("%H:%M:%S", time.gmtime(self.elapsed_time))

    def open(self, skip_files=False):
        """Execute pipeline processing.

        Args:
            skip_files (bool, optional): Whether to skip file operations.
                Defaults to False.
        """
        self.start_time = time.time()
        pipes, pconfig = self.get(self.name)
        self.pconfig = pconfig
        self._open(pipes, skip_files=skip_files)
        self.end_time = time.time()
        Log.info(f"Total running time: {self.elapsed_time_human}")

    @classmethod
    def _validate_config(cls, config: dict) -> bool:
        """Validate pipeline configuration.

        Args:
            config (dict): Configuration to validate

        Returns:
            bool: True if valid, raises exception otherwise

        Raises:
            ValueError: If configuration is invalid
        """
        if not config:
            raise ValueError("Empty pipeline configuration")
        if 'pipeline' not in config:
            raise ValueError("Missing pipeline section in configuration")
        return True

    def _setup_paths(self):
        """Set up input and output paths."""
        config = Config.get()
        self.out_path = config.get_value(get_keys().PROCESS_PATH)
        Files.make_dir(self.out_path)
        return config.get_value(get_keys().RAW_PATH), self.out_path

    def _setup_pipelines(self):
        """Configure pipeline instances from config."""
        configs = self.config.pipelines
        pipes = []
        for pconfig in configs:
            if self._validate_config(pconfig):
                name = pconfig['pipeline']['name']
                if name == self.name:
                    for pipe in pconfig['pipeline']['pipes']:
                        type = pipe['pipe']['type']
                        inst = Pipe.get_pipe(type)
                        pipes.append(inst(pipe['pipe'].get('config', {})))
                    self.register_pipeline(name, pipes,
                                           pconfig['pipeline']['config'])
                    break

    def _process_pipes(self, df, pipes, skip_files=False):
        """Process DataFrame through sequence of pipes.

        Args:
            df (pd.DataFrame): Input DataFrame to process
            pipes (list): List of pipe instances to execute
            skip_files (bool, optional): Whether to skip file operations.
                Defaults to False.

        Returns:
            pd.DataFrame: Processed DataFrame after running through all pipes

        Raises:
            RuntimeError: If pipe processing fails
        """
        _, config = self.get(self.name)
        Pipe.set_pipeline_config(config)
        for pipe in pipes:
            Log.info(f"Open -- {pipe.__class__.__name__}")
            try:
                df = pipe.flow(df, pipeline_config=config)
            except Exception as e:
                raise RuntimeError(
                    "Pipeline processing failed in "
                    f"{pipe.__class__.__name__}: {str(e)}") from e
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
            raise RuntimeError(f"Failed to save data: {str(e)}") from e

    def _process_file(self,
                      file: str,
                      pipes: list,
                      skip_files: bool = False) -> pd.DataFrame:
        """Process a single file through the pipeline.

        Args:
            file (str): Name of file to process
            pipes (list): List of pipe instances to execute
            skip_files (bool, optional): Whether to skip file operations.
                Defaults to False.

        Returns:
            pd.DataFrame: Processed DataFrame

        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If pipeline processing fails
        """
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
            raise RuntimeError(f"Pipeline processing failed: {str(e)}") from e

    def _open(self, pipes: list, skip_files: bool = False) -> None:
        """Open and process pipeline sequence.

        Args:
            pipes (list): List of pipe instances to execute
            skip_files (bool, optional): Whether to skip file operations.
                Defaults to False.

        Raises:
            RuntimeError: If pipeline execution fails
        """
        try:
            files = self.config.include_files or []
            for file in files:
                if not Files.is_excluded(file, self.config.exclude_files):
                    self._process_file(file, pipes, skip_files)
        except Exception as e:
            raise RuntimeError(f"Pipeline execution failed: {str(e)}") from e
