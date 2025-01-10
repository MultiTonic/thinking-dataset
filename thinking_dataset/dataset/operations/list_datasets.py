# @file thinking_dataset/datasets/operations/list_datasets.py
# @description Provides functionality for listing organization datasets.
# @version 1.0.0
# @license MIT

from .operation import Operation
from thinking_dataset.utils.log import Log


class ListDatasets(Operation):
    """
    A class to list datasets associated with the organization.
    """

    def execute(self):
        datasets = list(
            self.data_tonic.api.list_datasets(
                author=self.data_tonic.organization))
        Log.info(
            self.log,
            f"Number of {self.data_tonic.organization} datasets listed: "
            f"{len(datasets)}")

        return datasets
