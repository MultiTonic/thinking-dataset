"""
@file thinking_dataset/datasets/operations/list_datasets_operation.py
@description Provides functionality for listing organization datasets.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .base_operation import BaseOperation


class ListDatasets(BaseOperation):
    """
    A class to list datasets associated with the organization.

    Methods
    -------
    execute()
        Lists datasets associated with the organization.
    """

    def execute(self):
        """
        Lists datasets associated with the organization.

        Returns
        -------
        list
            A list of datasets associated with the organization.
        """
        datasets = list(
            self.data_tonic.list_datasets(author=self.data_tonic.organization))
        self.log_info(
            f"Number of {self.data_tonic.organization} datasets listed: "
            f"{len(datasets)}")

        return datasets
