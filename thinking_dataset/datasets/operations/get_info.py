"""
@file thinking_dataset/datasets/operations/get_info.py
@description Retrieves the dataset information.
@version 1.0.0
@license MIT
@param Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .base_operation import BaseOperation
from huggingface_hub.utils import RepositoryNotFoundError


class GetInfo(BaseOperation):
    """
    A class to retrieve dataset information.

    Methods
    -------
    execute(dataset_id)
        Retrieves the dataset information.
    """

    def execute(self, dataset_id):
        """
        Retrieves dataset information for the given dataset ID.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to retrieve information for.

        Returns
        -------
        dict
            Dataset information.
        """
        try:
            dataset_info = self.data_tonic.api.dataset_info(dataset_id)
            self.log_info("Retrieved dataset info: "
                          f"{dataset_info.card_data['description']}")
            return dataset_info
        except RepositoryNotFoundError as e:
            self.log_info(
                f"Error retrieving dataset info for {dataset_id}: {e}")
            raise
