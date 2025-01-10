# @file thinking_dataset/utils/load_dotenv.py
# @description Defines a decorator for loading env variables using dotenv.
# @version 1.0.0
# @license MIT

from functools import wraps
from dotenv import load_dotenv
from thinking_dataset.utils.command_utils import CommandUtils as utils


def dotenv(print=False):
    """
    A decorator to load environment variables using dotenv.
    Optionally prints the environment variables if print is True.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            log = kwargs['log']
            load_dotenv()
            dotenv = utils.load_dotenv()
            if print:
                utils.print_dotenv(dotenv, log)

            if not utils.verify_dotenv(dotenv, log):
                raise ValueError("Failed to validate environment variables.")

            kwargs['dotenv'] = dotenv
            return func(*args, **kwargs)

        return wrapper

    return decorator
