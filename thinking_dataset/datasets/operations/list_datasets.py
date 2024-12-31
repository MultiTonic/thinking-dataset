"""
@file thinking_dataset/datasets/operations/list_datasets.py
@description Provides functionality for listing organization datasets.
@version 1.0.0
@license MIT
"""

from .base_operation import BaseOperation
from ...utilities.log import Log


class ListDatasets(BaseOperation):
    """
    A class to list datasets associated with the organization.
    """

    def execute(self):
        """
        Lists datasets associated with the organization.
        """
        datasets = list(
            self.data_tonic.api.list_datasets(
                author=self.data_tonic.organization))
        Log.info(
            self.log,
            f"Number of {self.data_tonic.organization} datasets listed: "
            f"{len(datasets)}")

        return datasets
