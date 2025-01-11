"""
@file thinking_dataset/datasets/operations/get_license.py
@description Operation to retrieve dataset license information.
@version 1.0.0
@license MIT
"""

from .operation import Operation


class GetLicense(Operation):
    """
    Operation class to retrieve dataset license information.
    """

    def execute(self):
        """
        Retrieves the license information of the dataset.
        """
        dataset_info = self.dt.get_dataset_info()
        license_info = dataset_info.card_data.get('license', None)
        self.log_info(f"Dataset license: {license_info}")
        return license_info
