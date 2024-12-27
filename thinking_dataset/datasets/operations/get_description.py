"""
@file thinking_dataset/datasets/operations/get_description.py
@description Operation to retrieve dataset description.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .base_operation import BaseOperation


class GetDescription(BaseOperation):
    """
    Operation class to retrieve dataset description.
    """

    def execute(self):
        """
        Retrieves the description of the dataset.

        Returns
        -------
        str
            The description of the dataset.
        """
        dataset_info = self.data_tonic.get_dataset_info()
        description = dataset_info.card_data.get('description', '')
        self.log_info(f"Dataset description: {description}")
        return description
