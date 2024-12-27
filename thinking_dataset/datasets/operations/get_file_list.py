"""
@file thinking_dataset/datasets/operations/get_file_list.py
@description Operation to retrieve list of dataset files.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

from .base_operation import BaseOperation


class GetFileList(BaseOperation):
    """
    A class to retrieve the list of files in the dataset.
    """

    def execute(self, dataset_id):
        """
        Retrieves the list of files in the dataset.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to retrieve the file list for.

        Returns
        -------
        list
            A list of files in the dataset.
        """
        dataset_info = self.data_tonic.get_dataset_info(dataset_id)
        file_list = dataset_info.siblings
        self.log_info(f"Dataset files: {file_list}")
        return file_list
