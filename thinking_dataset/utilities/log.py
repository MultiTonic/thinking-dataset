"""
@file thinking_dataset/utilities/log.py
@description Defines the Log class for unified logging.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import logging
from rich.logging import RichHandler
from rich.traceback import install

# Install rich traceback handler for pretty errors
install(show_locals=True)


class Log:
    """
    A class for unified logging across the project.
    """

    @staticmethod
    def setup(name):
        """
        Sets up a logger with the specified name using RichHandler.
        """
        logger = logging.getLogger(name)
        if not logger.hasHandlers():
            rich_handler = RichHandler(show_path=True,
                                       tracebacks_show_locals=True,
                                       tracebacks_word_wrap=False)
            logger.addHandler(rich_handler)
            logger.setLevel(logging.INFO)
        return logger

    @staticmethod
    def info(logger, message):
        """
        Logs an informational message.
        """
        logger.info(message, stacklevel=2)

    @staticmethod
    def error(logger, message, exc_info=None):
        """
        Logs an error message with an optional exception.
        """
        logger.error(message, exc_info=exc_info, stacklevel=2)

    @staticmethod
    def warn(logger, message):
        """
        Logs a warning message.
        """
        logger.warning(message, stacklevel=2)
