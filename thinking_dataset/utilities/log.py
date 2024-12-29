"""
@file thinking_dataset/utilities/log.py
@description Defines the Log class for unified logging.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import logging


class Log:
    """
    A class for unified logging across the project.
    """

    @staticmethod
    def setup(name):
        """
        Sets up a logger with the specified name.

        Parameters
        ----------
        name : str
            The name of the logger.

        Returns
        -------
        logger : Logger
            A configured logger.
        """
        logger = logging.getLogger(name)
        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    @staticmethod
    def info(logger, message):
        """
        Logs an informational message.

        Parameters
        ----------
        logger : Logger
            The logger instance to use for logging.
        message : str
            The message to log.
        """
        logger.info(message)
        raise RuntimeError(message)

    @staticmethod
    def error(logger, message):
        """
        Logs an error message.

        Parameters
        ----------
        logger : Logger
            The logger instance to use for logging.
        message : str
            The message to log.
        """
        logger.error(message)
        raise RuntimeError(message)

    @staticmethod
    def warn(logger, message):
        """
        Logs a warning message.

        Parameters
        ----------
        logger : Logger
            The logger instance to use for logging.
        message : str
            The message to log.
        """
        logger.warning(message)
        raise RuntimeError(message)
