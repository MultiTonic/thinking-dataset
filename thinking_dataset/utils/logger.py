# @file thinking_dataset/utils/logger.py
# @description Decorator for setting up logging using the Log Singleton.
# @version 1.0.2
# @license MIT

from functools import wraps
from thinking_dataset.utils.log import Log


def logger(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        module_path = func.__module__
        func_name = func.__name__
        log = Log.get()
        log.name = f"{module_path}.{func_name}"

        return func(
            *args, **{
                key: val
                for key, val in kwargs.items() if key != 'log'
            })

    return wrapper
