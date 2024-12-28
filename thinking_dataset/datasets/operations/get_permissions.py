"""
@file thinking_dataset/datasets/operations/get_permissions.py
@description Operation to check dataset permissions.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .base_operation import BaseOperation


class GetPermissions(BaseOperation):
    """
    Operation class to check dataset permissions.
    """

    def execute(self, dataset_id):
        """
        Checks the permissions of the dataset.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to check permissions for.

        Returns
        -------
        bool
            True if the dataset is private, False otherwise.
        """
        dataset_info = self.data_tonic.get_dataset_info(dataset_id)
        self.log_info(f"Dataset permissions: {dataset_info.private}")
        return dataset_info.private
