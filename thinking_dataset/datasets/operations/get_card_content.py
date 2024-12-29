"""
@file thinking_dataset/datasets/operations/get_card_content.py
@description Operation to retrieve dataset card content.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .base_operation import BaseOperation


class GetCardContent(BaseOperation):
    """
    Operation class to retrieve dataset card content.
    """

    def execute(self, dataset_id):
        """
        Retrieves card content of the dataset.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to retrieve card content for.

        Returns
        -------
        dict
            The card content of the dataset.
        """
        dataset_info = self.data_tonic.get_dataset_info(dataset_id)
        card_content = dataset_info.card_data
        self.log_info(f"Dataset card data: {card_content}")
        return card_content
