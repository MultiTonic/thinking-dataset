# @file project_root/thinking_dataset/pipeworks/pipelines/pipeline.py
# @description Defines the Pipeline class for managing data processing.
# @version 1.2.0
# @license MIT

import os
import time
from ...io.files import Files
from ..pipes.pipe import Pipe
from ...utilities.log import Log
from ...config.config import Config
from ...utilities.text_utils import TextUtils as Text
from ...utilities.command_utils import CommandUtils as Utils
from ...db.database import Database


class Pipeline:
    pipelines = []

    def __init__(self, log, name=None):
        self.config = Config.get_config()
        self.log = log
        self.input_path, self.output_path = self._setup_paths()
        self.name = name
        self._setup_pipelines()

    def _setup_paths(self):
        files = Files(self.config)
        self.output_path = files.get_processed_path()
        files.make_dir(self.output_path, self.log)
        return files.get_raw_path(), self.output_path

    def _setup_pipelines(self):
        configs = self.config.pipelines
        pipes = []
        for config in configs:
            name = config['pipeline']['name']
            if name == self.name:
                for pipe in config['pipeline']['pipes']:
                    pipe_type = pipe['pipe']['type']
                    instance = Pipe.get_pipe(pipe_type)
                    pipes.append(instance(pipe['pipe'].get('config', {})))
                Pipeline.pipelines.append(
                    (name, pipes, config['pipeline']['config']))
                break

    def _process_pipes(self, df, pipes, log):
        for pipe in pipes:
            Log.info(log, f"Open -- {pipe.__class__.__name__}")
            df = pipe.flow(df, log)
        return df

    def _save_data(self, df, file_path, log):
        Utils.to(df, file_path, self.config.dataset_type)
        file_size = os.path.getsize(file_path)
        human_readable_file_size = Text.human_readable_size(file_size)
        Log.info(
            log, f"Data processed and saved to {file_path} "
            f"(Size: {human_readable_file_size})")

    def _process_file(self, file, file_pattern, pipes, log):
        input_file = Files.get_path(self.input_path, file)
        Log.info(log, f"Processing file: {input_file}")

        if not Files.exists(input_file):
            Log.warn(log, f"File not found: {input_file}")
            return

        df = Utils.read_data(input_file, self.config.dataset_type)
        df = self._process_pipes(df, pipes, log)
        file_name = f"processed_{file}"
        file_path = Files.get_path(self.output_path, file_name)
        self._save_data(df, file_path, log)

    def _open(self, pipes, config, log, skip_files=False):
        if skip_files:
            db_url = self.config.database_url
            db = Database(url=db_url)
            db.process(pipes, log, self.output_path, self.config.dataset_type)
        else:
            files_to_process = self.config.include_files or []
            for file in files_to_process:
                if not Files.is_excluded(file, self.config.exclude_files, log):
                    self._process_file(file, config.get("file"), pipes, log)

    def get(self, name):
        for name, pipes, config in Pipeline.pipelines:
            if name == name:
                return pipes, config
        raise ValueError(f"Pipeline '{name}' not found")

    def open(self, skip_files=False):
        start_time = time.time()
        pipes, pipe_config = self.get(self.name)
        self._open(pipes, pipe_config, self.log, skip_files=skip_files)
        end_time = time.time()
        elapsed_time = end_time - start_time
        human_readable_time = time.strftime("%H:%M:%S",
                                            time.gmtime(elapsed_time))
        Log.info(self.log, f"Total running time: {human_readable_time}")
