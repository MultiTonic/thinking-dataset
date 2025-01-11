"""
@file thinking_dataset/datasets/operations/get_description.py
@description Operation to retrieve dataset description.
@version 1.0.0
@license MIT
"""

from .operation import Operation


class GetDescription(Operation):
    """
    Operation class to retrieve dataset description.
    """

    def execute(self):
        """
        Retrieves the description of the dataset.
        """
        dataset_info = self.dt.get_dataset_info()
        description = dataset_info.card_data.get('description', '')
        self.log_info(f"Dataset description: {description}")
        return description
