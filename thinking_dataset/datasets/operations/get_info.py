"""
@file thinking_dataset/datasets/operations/get_info.py
@description Retrieves the dataset information.
@version 1.0.0
@license MIT
"""

from .base_operation import BaseOperation
from huggingface_hub.utils import RepositoryNotFoundError
from ...utilities.log import Log


class GetInfo(BaseOperation):
    """
    A class to retrieve dataset information.
    """

    def execute(self, dataset_id):
        """
        Retrieves dataset information for the given dataset ID.
        """
        try:
            dataset_info = self.data_tonic.api.dataset_info(dataset_id)
            description = dataset_info.card_data.get(
                'description', 'No description available')
            Log.info(self.log, f"Retrieved dataset info: {description}")
            return dataset_info
        except RepositoryNotFoundError as e:
            Log.error(self.log,
                      f"Error retrieving dataset info for {dataset_id}: {e}")
            raise
