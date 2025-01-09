# @file thinking_dataset/utilities/log.py
# @description Defines the Log class for unified logging.
# @version 1.0.0
# @license MIT

import logging
import sys
import inspect

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class Log:
    """
    A class for unified logging across the project.
    """

    _instance = None

    @staticmethod
    def _get_name():
        frame = inspect.stack()[2]
        module = inspect.getmodule(frame[0])
        module_name = module.__name__ if module else 'thinking-dataset'
        class_name = frame[3]
        return f'{module_name}.{class_name}'

    @staticmethod
    def _setup():
        logging.basicConfig(level=logging.INFO,
                            format=LOG_FORMAT,
                            datefmt='%Y.%m.%d:%H:%M:%S',
                            handlers=[logging.StreamHandler(sys.stdout)])

        sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
        sqlalchemy_logger.setLevel(logging.INFO)
        sqlalchemy_logger.propagate = False

        Log._instance = logging.getLogger("thinking-dataset")

    @staticmethod
    def get():
        if Log._instance is None:
            Log._setup()
        return Log._instance

    @staticmethod
    def info(message):
        log = Log.get()
        log.name = Log._get_name()
        log.info(message)

    @staticmethod
    def error(message, exc_info=None):
        log = Log.get()
        log.name = Log._get_name()
        log.error(message, exc_info=exc_info)

    @staticmethod
    def warn(message):
        log = Log.get()
        log.name = Log._get_name()
        log.warning(message)

    @staticmethod
    def get_handler():
        return logging.StreamHandler(sys.stdout)
