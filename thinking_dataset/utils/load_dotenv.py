# @file thinking_dataset/utils/load_dotenv.py
# @description Defines a decorator for loading env variables using dotenv.
# @version 1.0.2
# @license MIT

from functools import wraps
from dotenv import load_dotenv
from thinking_dataset.utils.command_utils import CommandUtils as utils
from thinking_dataset.utils.log import Log


def dotenv(print=False):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            load_dotenv()
            dotenv = utils.load_dotenv()
            log = Log.get()

            if print:
                utils.print_dotenv(dotenv, log)

            if not utils.verify_dotenv(dotenv, log):
                raise ValueError("Failed to validate environment variables.")

            return func(
                *args, **{
                    key: val
                    for key, val in kwargs.items() if key != 'log'
                })

        return wrapper

    return decorator
