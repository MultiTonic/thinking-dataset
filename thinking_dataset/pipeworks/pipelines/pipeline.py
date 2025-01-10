# @file thinking_dataset/pipeworks/pipelines/pipeline.py
# @description Manages the flow of data through the pipeline.
# @version 1.2.15
# @license MIT

import os
import time
from ...io.files import Files
from ..pipes.pipe import Pipe
from thinking_dataset.utils.log import Log
import thinking_dataset.config as conf
from thinking_dataset.utils.text_utils import TextUtils as Text
from thinking_dataset.utils.command_utils import CommandUtils as utils


class Pipeline:
    pipelines = []

    def __init__(self, name=None):
        self.config = conf.initialize()
        self.in_path, self.out_path = self._setup_paths()
        self.name = name
        self._setup_pipelines()

    def _setup_paths(self):
        config = conf.Config.get()
        self.out_path = config.get_value(conf.get_keys().PROCESS_PATH)
        Files.make_dir(self.out_path)
        return config.get_value(conf.get_keys().RAW_PATH), self.out_path

    def _setup_pipelines(self):
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

    def _process_pipes(self, df, pipes):
        for pipe in pipes:
            Log.info(f"Open -- {pipe.__class__.__name__}")
            df = pipe.flow(df)
        return df

    def _save_data(self, df, file_path):
        utils.to(df, file_path, self.config.dataset_type)
        file_size = os.path.getsize(file_path)
        human_readable_file_size = Text.human_readable_size(file_size)
        Log.info(f"Data process and saved to {file_path} "
                 f"(Size: {human_readable_file_size})")

    def _process_file(self, file, pipes, skip_files=False):
        input_file = Files.get_file_path(self.in_path, file)
        Log.info(f"Processing file: {input_file}")

        if not skip_files:
            if not Files.exists(input_file):
                raise FileNotFoundError(f"File not found: {input_file}")

        df = utils.read_data(input_file, self.config.dataset_type)
        df = self._process_pipes(df, pipes)

        if not skip_files:
            base_name, ext = os.path.splitext(file)
            file_name = f"{base_name}{ext}"
            file_path = Files.get_file_path(self.out_path, file_name)
            self._save_data(df, file_path)

    def _open(self, pipes, skip_files=False):
        files = self.config.include_files or []
        for file in files:
            if not Files.is_excluded(file, self.config.exclude_files):
                self._process_file(file, pipes, skip_files)

    def get(self, name):
        for pname, pipes, pconfig in Pipeline.pipelines:
            if pname == name:
                return pipes, pconfig
        raise ValueError(f"Pipeline '{name}' not found")

    def open(self, skip_files=False):
        start_time = time.time()
        pipes, config = self.get(self.name)
        self._open(pipes, skip_files=skip_files)
        end_time = time.time()
        elapsed_time = end_time - start_time
        human_readable_time = time.strftime("%H:%M:%S",
                                            time.gmtime(elapsed_time))
        Log.info(f"Total running time: {human_readable_time}")
