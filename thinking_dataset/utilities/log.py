"""
@file thinking_dataset/utilities/log.py
@description Defines the Log class for unified logging.
@version 1.0.0
@license MIT
"""

import logging
import sys

# Customize the log format to include a timestamp
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class Log:
    """
    A class for unified logging across the project.
    """

    @staticmethod
    def setup(name):
        """
        Sets up a logger with the specified name using standard logging.
        """
        logging.basicConfig(level=logging.INFO,
                            format=LOG_FORMAT,
                            datefmt='%Y-%m-%d %H:%M:%S',
                            handlers=[logging.StreamHandler(sys.stdout)])

        # Set up SQLAlchemy to use the standard logging
        sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
        sqlalchemy_logger.setLevel(logging.INFO)
        sqlalchemy_logger.propagate = False

        return logging.getLogger(name)

    @staticmethod
    def info(log, message):
        """
        Logs an informational message.
        """
        log.info(message)

    @staticmethod
    def error(log, message, exc_info=None):
        """
        Logs an error message with an optional exception.
        """
        log.error(message, exc_info=exc_info)

    @staticmethod
    def warn(log, message):
        """
        Logs a warning message.
        """
        log.warning(message)

    @staticmethod
    def get_handler():
        """
        Returns the standard logging handler.
        """
        return logging.StreamHandler(sys.stdout)
