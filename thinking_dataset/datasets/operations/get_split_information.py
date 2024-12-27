"""
@file thinking_dataset/datasets/operations/get_split_information.py
@description Operation to retrieve dataset split information.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .base_operation import BaseOperation


class GetSplitInformation(BaseOperation):
    """
    Operation class to retrieve dataset split information.
    """

    def execute(self):
        """
        Retrieves the split information of the dataset.

        Returns
        -------
        list
            A list of splits in the dataset.
        """
        dataset_info = self.data_tonic.get_dataset_info()
        splits = dataset_info.card_data['dataset_info']['splits']
        self.log_info(f"Dataset splits: {splits}")
        return splits
