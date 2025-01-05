# @file project_root/thinking_dataset/pipeworks/pipelines/pipeline.py
# @description Defines the Pipeline class for managing data processing.
# @version 1.0.0
# @license MIT

import os
import time
from ...io.files import Files
from ..pipes.pipe import Pipe
from ...utilities.log import Log
from ...config.config import Config
from ...utilities.text_utils import TextUtils as Text
from ...utilities.command_utils import CommandUtils as Utils


class Pipeline:
    pipelines = []

    def __init__(self, log):
        self.config = Config.get_config()
        self.log = log
        self.input_path, self.output_path = self._setup_paths()
        self._setup_pipelines()

    def _setup_paths(self):
        files = Files(self.config)
        input_path = files.get_raw_path()
        output_path = files.get_processed_path()
        files.make_dir(output_path, self.log)
        return input_path, output_path

    def _setup_pipelines(self):
        configs = self.config.PIPELINES
        for config in configs:
            pipes = []
            for pipe in config['pipeline']['pipes']:
                pipe_type = pipe['pipe']['type']
                instance = Pipe.get_pipe(pipe_type)
                pipes.append(instance(pipe['pipe'].get('config', {})))
            Pipeline.pipelines.append((pipes, config['pipeline']['config']))

    def _prepare_file_name(self, file, prepare_file):
        file_root, file_ext = os.path.splitext(file)
        return prepare_file.format(file_base=file_root, file_ext=file_ext)

    def _read_data(self, input_file):
        return Utils.read_data(input_file, self.config.DATASET_TYPE)

    def _process_pipes(self, df, pipes, file, log):
        for pipe in pipes:
            Log.info(log, f"Open -- {pipe.__class__.__name__} on {file}")
            df = pipe.flow(df, log)
        return df

    def _save_data(self, df, file_path, log):
        Utils.to(df, file_path, self.config.DATASET_TYPE)
        file_size = os.path.getsize(file_path)
        human_readable_file_size = Text.human_readable_size(file_size)
        Log.info(
            log, f"Data processed and saved to {file_path} "
            f"(Size: {human_readable_file_size})")

    def _process_file(self, file, prepare_file, pipes, log):
        input_file = Files.get_path(self.input_path, file)
        Log.info(log, f"Processing file: {input_file}")

        if not Files.exists(input_file):
            Log.warn(log, f"File not found: {input_file}")
            return

        file_name = self._prepare_file_name(file, prepare_file)
        file_path = Files.get_path(self.output_path, file_name)
        df = self._read_data(input_file)
        df = self._process_pipes(df, pipes, file, log)
        self._save_data(df, file_path, log)

    def _open(self, pipes, config, log):
        prepare_file = config["prepare_file"]

        for file in self.config.INCLUDE_FILES:
            if not Files.is_excluded(file, self.config.EXCLUDE_FILES, log):
                self._process_file(file, prepare_file, pipes, log)

    def open(self):
        start_time = time.time()
        for pipes, pipe_config in Pipeline.pipelines:
            self._open(pipes, pipe_config, self.log)
        end_time = time.time()
        elapsed_time = end_time - start_time
        human_readable_time = time.strftime("%H:%M:%S",
                                            time.gmtime(elapsed_time))
        Log.info(self.log, f"Total running time: {human_readable_time}")
