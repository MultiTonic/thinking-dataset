"""
@file thinking_dataset/utilities/logger.py
@description Defines a decorator for setting up logging.
@version 1.0.0
@license MIT
"""

from functools import wraps
from ..utilities.log import Log


def logger(func):
    """
    A decorator to set up logging for a function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        module_path = func.__module__
        func_name = func.__name__
        log = Log.setup(f"{module_path}.{func_name}")
        kwargs['log'] = log
        return func(*args, **kwargs)

    return wrapper
