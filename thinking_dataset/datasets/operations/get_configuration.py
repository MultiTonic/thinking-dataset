"""
@file thinking_dataset/datasets/operations/get_configuration.py
@description Operation to retrieve dataset configurations.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .base_operation import BaseOperation


class GetConfiguration(BaseOperation):
    """
    Operation class to retrieve dataset configurations.
    """

    def execute(self):
        """
        Retrieves the configurations of the dataset.

        Returns
        -------
        list
            A list of configurations for the dataset.
        """
        dataset_info = self.data_tonic.get_dataset_info()
        configs = dataset_info.card_data.get('configs', [])
        self.log_info(f"Dataset configurations: {configs}")
        return configs