"""
@file thinking_dataset/datasets/operations/get_metadata.py
@description Operation to retrieve dataset metadata.
@version 1.0.0
@license MIT
"""

from .operation import Operation


class GetMetadata(Operation):
    """
    Operation class to retrieve dataset metadata.
    """

    def execute(self):
        """
        Retrieves metadata about the dataset.
        """
        dataset_info = self.dt.get_dataset_info()
        self.log_info(f"Dataset metadata: {dataset_info}")
        return dataset_info
