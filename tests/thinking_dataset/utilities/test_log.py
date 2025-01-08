"""
@file tests/thinking_dataset/utilities/test_log.py
@description Unit tests for the Log class.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
import logging
from thinking_dataset.utilities.log import Log


@pytest.fixture
def test_logger():
    return Log._setup("test_logger")


def test_setup_logger(test_logger):
    assert isinstance(test_logger, logging.Logger)
    assert test_logger.name == "test_logger"


def test_info_logging(test_logger, caplog):
    log_message = "Info message"
    with caplog.at_level(logging.INFO):
        Log.info(test_logger, log_message)
    assert log_message in caplog.text


def test_error_logging(test_logger, caplog):
    log_message = "Error message"
    with caplog.at_level(logging.ERROR):
        Log.error(test_logger, log_message)
    assert log_message in caplog.text


def test_warn_logging(test_logger, caplog):
    log_message = "Warning message"
    with caplog.at_level(logging.WARNING):
        Log.warn(test_logger, log_message)
    assert log_message in caplog.text


if __name__ == "__main__":
    pytest.main()
