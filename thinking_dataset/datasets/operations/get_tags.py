"""
@file thinking_dataset/datasets/operations/get_tags.py
@description Operation to retrieve tags associated with the dataset.
@version 1.0.0
@license MIT
"""

from .base_operation import Operation


class GetTags(Operation):
    """
    Operation class to retrieve tags associated with the dataset.
    """

    def execute(self, dataset_id):
        """
        Retrieves tags associated with the dataset.
        """
        dataset_info = self.data_tonic.get_dataset_info(dataset_id)
        tags = dataset_info.tags
        self.log_info(f"Dataset tags: {tags}")
        return tags
