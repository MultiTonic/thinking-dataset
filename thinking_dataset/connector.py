"""
@file thinking_dataset/connector.py
@description Connector class for interacting with Hugging Face API.
@version 1.0.0
@license MIT
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from huggingface_hub import HfApi
from loguru import logger


class Connector:
    """
    A class used to interact with the Hugging Face API.

    Attributes
    ----------
    api : HfApi
        An instance of the Hugging Face API.
    token : str
        The API token for authentication.

    Methods
    -------
    log_info(message)
        Logs an info message using the logger.
    get_whoami()
        Retrieves information about the authenticated user.
    list_datasets(author=None, search=None)
        Lists datasets associated with the specified author or search query.
    get_dataset_info(dataset_id)
        Retrieves metadata about the specified dataset.
    """

    def __init__(self, token):
        """
        Constructs all the necessary attributes for the Connector object.

        Parameters
        ----------
        token : str
            The API token for authentication.
        """
        self.api = HfApi(token=token)
        self.token = token

    @staticmethod
    def log_info(message):
        """
        Logs an info message using the logger.

        Parameters
        ----------
        message : str
            The message to log.
        """
        logger.info(message)

    def get_whoami(self):
        """
        Retrieves information about the authenticated user.

        Returns
        -------
        dict
            Information about the authenticated user.
        """
        return self.api.whoami()

    def list_datasets(self, author=None, search=None):
        """
        Lists datasets associated with the specified author or search query.

        Parameters
        ----------
        author : str, optional
            The author of the datasets to list (default is None).
        search : str, optional
            The search query to filter datasets (default is None).

        Returns
        -------
        list
            A list of datasets matching the criteria.
        """
        return self.api.list_datasets(author=author, search=search)

    def get_dataset_info(self, dataset_id):
        """
        Retrieves metadata about the specified dataset.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to retrieve metadata for.

        Returns
        -------
        DatasetInfo
            Metadata about the specified dataset.
        """
        return self.api.dataset_info(dataset_id)
