"""
@file project_root/thinking_dataset/pipeworks/pipes/pipe.py
@description Defines the base Pipe class.
@version 1.0.0
@license MIT
"""


class Pipe:

    def __init__(self, pipe_class, config):
        self.pipe = pipe_class(config)

    def flow(self, df, log):
        return self.pipe.flow(df, log)
