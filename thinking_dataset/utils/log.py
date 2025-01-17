# @file thinking_dataset/utils/log.py
# @description Defines the Log class for unified logging.
# @version 1.0.10
# @license MIT

import sys
import inspect
import logging as log
import functools

LF = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class Log:
    """
    A class for unified logging across the project.
    """

    _instance = None
    _level = log.INFO

    CRITICAL = log.CRITICAL
    ERROR = log.ERROR
    WARNING = log.WARNING
    INFO = log.INFO
    DEBUG = log.DEBUG
    NOTSET = log.NOTSET

    @staticmethod
    def _get_name():
        frame = inspect.stack()[2]
        module = inspect.getmodule(frame[0])
        module_name = module.__name__ if module else 'thinking-dataset'
        class_name = frame[3]
        return f'{module_name}.{class_name}'

    @staticmethod
    def _setup():
        log.basicConfig(level=Log._level,
                        format=LF,
                        datefmt='%Y.%m.%d:%H:%M:%S',
                        handlers=[log.StreamHandler(sys.stdout)])

        Log._instance = log.getLogger("thinking-dataset")
        Log._instance.setLevel(Log._level)

    @staticmethod
    def get():
        if Log._instance is None:
            Log._setup()
        return Log._instance

    @staticmethod
    def set_level(level):
        Log._level = level
        if Log._instance:
            Log._instance.setLevel(Log._level)
            logger = log.getLogger('thinking-dataset')
            logger.setLevel(Log._level)

    @staticmethod
    def info(message):
        if Log._level <= log.INFO:
            logger = Log.get()
            logger.name = Log._get_name()
            logger.info(message)

    @staticmethod
    def error(message, exc_info=None):
        if Log._level <= log.ERROR:
            logger = Log.get()
            logger.name = Log._get_name()
            logger.error(message, exc_info=exc_info)

    @staticmethod
    def warn(message):
        if Log._level <= log.WARNING:
            logger = Log.get()
            logger.name = Log._get_name()
            logger.warning(message)

    @staticmethod
    def debug(message):
        if Log._level <= log.DEBUG:
            logger = Log.get()
            logger.name = Log._get_name()
            logger.debug(message)

    @staticmethod
    def get_handler():
        return log.StreamHandler(sys.stdout)

    @staticmethod
    def level(level):

        def decorator(func):

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                prev_level = Log._level
                Log.set_level(level)
                try:
                    return func(*args, **kwargs)
                finally:
                    Log.set_level(prev_level)

            return wrapper

        return decorator
