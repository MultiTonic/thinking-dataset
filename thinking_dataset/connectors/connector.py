"""
@file thinking_dataset/connector.py
@description Connector class for interacting with Hugging Face API.
@version 1.0.0
@license MIT
"""

from huggingface_hub import HfApi
from ..utilities.log import Log


class Connector:
    """
    A class used to interact with the Hugging Face API.
    """

    def __init__(self, token):
        """
        Constructs all the necessary attributes for the Connector object.
        """
        self.api = HfApi(token=token)
        self.token = token
        self.log = Log.setup(self.__class__.__name__)
