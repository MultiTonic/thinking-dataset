"""
@file thinking_dataset/datasets/operations/get_tags.py
@description Operation to retrieve tags associated with the dataset.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .base_operation import BaseOperation


class GetTags(BaseOperation):
    """
    Operation class to retrieve tags associated with the dataset.
    """

    def execute(self, dataset_id):
        """
        Retrieves tags associated with the dataset.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to retrieve tags for.

        Returns
        -------
        list
            A list of tags associated with the dataset.
        """
        dataset_info = self.data_tonic.get_dataset_info(dataset_id)
        tags = dataset_info.tags
        self.log_info(f"Dataset tags: {tags}")
        return tags
