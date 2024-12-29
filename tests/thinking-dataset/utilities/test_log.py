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
    return Log.setup("test_logger")


def test_setup_logger(test_logger):
    assert isinstance(test_logger, logging.Logger)
    assert test_logger.name == "test_logger"


def test_info_logging(test_logger):
    with pytest.raises(RuntimeError) as log:
        Log.info(test_logger, "Info message")
    assert str(log.value) == "Info message"


def test_error_logging(test_logger):
    with pytest.raises(RuntimeError) as log:
        Log.error(test_logger, "Error message")
    assert str(log.value) == "Error message"


def test_warn_logging(test_logger):
    with pytest.raises(RuntimeError) as log:
        Log.warn(test_logger, "Warning message")
    assert str(log.value) == "Warning message"


if __name__ == "__main__":
    pytest.main()
