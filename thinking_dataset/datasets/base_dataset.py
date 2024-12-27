"""
@file thinking_dataset/datasets/base_dataset.py
@description Provides common functionalities for dataset operations.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""


class BaseDataset:
    """
    A base class that provides common dataset operations and
    logging functionalities.

    Attributes
    ----------
    data_tonic : DataTonic
        An instance of the DataTonic class containing dataset
        and organization information.

    Methods
    -------
    get_dataset_info(dataset_id=None)
        Retrieves metadata about the dataset associated with
        the DataTonic instance.
    log_info(message)
        Logs an info message using the logger provided by the
        DataTonic instance.
    """

    def __init__(self, data_tonic):
        """
        Constructs all the necessary attributes for the BaseDataset object.

        Parameters
        ----------
        data_tonic : DataTonic
            The DataTonic instance containing dataset and
            organization information.
        """
        self.data_tonic = data_tonic

    def get_dataset_info(self, dataset_id=None):
        """
        Retrieves metadata about the dataset associated with
        the DataTonic instance.

        Parameters
        ----------
        dataset_id : str, optional
            The ID of the dataset to retrieve information for.

        Returns
        -------
        DatasetInfo
            Metadata about the specified dataset.
        """
        if dataset_id:
            return self.data_tonic.get_dataset_info(dataset_id)
        return self.data_tonic.get_dataset_info(
            f"{self.data_tonic.organization}/{self.data_tonic.dataset}")

    def log_info(self, message):
        """
        Logs an info message using the logger provided by
        the DataTonic instance.

        Parameters
        ----------
        message : str
            The message to log.
        """
        self.data_tonic.log_info(message)
