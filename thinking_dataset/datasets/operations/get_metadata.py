"""
@file thinking_dataset/datasets/operations/get_metadata.py
@description Operation to retrieve dataset metadata.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .base_operation import BaseOperation


class GetMetadata(BaseOperation):
    """
    Operation class to retrieve dataset metadata.
    """

    def execute(self):
        """
        Retrieves metadata about the dataset.

        Returns
        -------
        DatasetInfo
            Metadata about the specified dataset.
        """
        dataset_info = self.data_tonic.get_dataset_info()
        self.log_info(f"Dataset metadata: {dataset_info}")
        return dataset_info
