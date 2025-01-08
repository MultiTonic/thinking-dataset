# @file thinking_dataset/datasets/operations/get_info.py
# @description Retrieves the dataset information.
# @version 1.0.0
# @license MIT

from .operation import Operation
from huggingface_hub.utils import RepositoryNotFoundError
from ...utilities.log import Log


class GetInfo(Operation):
    """
    A class to retrieve dataset information.
    """

    def execute(self, repo_id):
        try:
            dataset_info = self.data_tonic.api.dataset_info(repo_id)
            description = dataset_info.card_data.get(
                'description', 'No description available')
            Log.info(f"Retrieved dataset info: {description}")
            return dataset_info
        except RepositoryNotFoundError as e:
            Log.error(f"Error retrieving dataset info for {repo_id}: {e}")
            raise
