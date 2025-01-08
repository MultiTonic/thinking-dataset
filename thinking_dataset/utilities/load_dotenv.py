# @file thinking_dataset/utilities/load_dotenv.py
# @description Defines a decorator for loading env variables using dotenv.
# @version 1.0.0
# @license MIT

from functools import wraps
from dotenv import load_dotenv
from ..utilities.command_utils import CommandUtils as Utils


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
            dotenv = Utils.load_dotenv()
            if print:
                Utils.print_dotenv(dotenv, log)

            if not Utils.verify_dotenv(dotenv, log):
                raise ValueError("Failed to validate environment variables.")

            kwargs['dotenv'] = dotenv
            return func(*args, **kwargs)

        return wrapper

    return decorator
