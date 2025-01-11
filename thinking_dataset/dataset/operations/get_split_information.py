"""
@file thinking_dataset/datasets/operations/get_split_information.py
@description Operation to retrieve dataset split information.
@version 1.0.0
@license MIT
"""

from .operation import Operation


class GetSplitInformation(Operation):
    """
    Operation class to retrieve dataset split information.
    """

    def execute(self):
        """
        Retrieves the split information of the dataset.
        """
        dataset_info = self.dt.get_dataset_info()
        splits = dataset_info.card_data['dataset_info']['splits']
        self.log_info(f"Dataset splits: {splits}")
        return splits
