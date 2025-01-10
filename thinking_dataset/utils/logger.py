"""
@file thinking_dataset/utils/logger.py
@desc Decorator for setting up logging using the Log Singleton.
@version 1.0.1
@license MIT
"""

from functools import wraps
from thinking_dataset.utils.log import Log


def logger(func):
    """
    A decorator to set up logging for a function using the Log Singleton.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        module_path = func.__module__
        func_name = func.__name__
        log = Log.get()
        log.name = f"{module_path}.{func_name}"
        kwargs['log'] = log
        return func(*args, **kwargs)

    return wrapper
