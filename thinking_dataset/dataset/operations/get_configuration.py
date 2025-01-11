"""
@file thinking_dataset/datasets/operations/get_configuration.py
@description Operation to retrieve dataset configurations.
@version 1.0.0
@license MIT
"""

from .operation import Operation


class GetConfiguration(Operation):
    """
    Operation class to retrieve dataset configurations.
    """

    def execute(self):
        """
        Retrieves the configurations of the dataset.
        """
        dataset_info = self.dt.get_dataset_info()
        configs = dataset_info.card_data.get('configs', [])
        self.log_info(f"Dataset configurations: {configs}")
        return configs
