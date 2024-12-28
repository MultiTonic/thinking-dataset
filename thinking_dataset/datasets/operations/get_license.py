"""
@file thinking_dataset/datasets/operations/get_license.py
@description Operation to retrieve dataset license information.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .base_operation import BaseOperation


class GetLicense(BaseOperation):
    """
    Operation class to retrieve dataset license information.
    """

    def execute(self):
        """
        Retrieves the license information of the dataset.

        Returns
        -------
        str
            The license information of the dataset.
        """
        dataset_info = self.data_tonic.get_dataset_info()
        license_info = dataset_info.card_data.get('license', None)
        self.log_info(f"Dataset license: {license_info}")
        return license_info