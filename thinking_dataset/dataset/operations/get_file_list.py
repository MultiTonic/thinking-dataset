# @file thinking_dataset/datasets/operations/get_file_list.py
# @description Operation to retrieve list of dataset virtual files.
# @version 1.0.8
# @license MIT

from .operation import Operation
from thinking_dataset.utils.log import Log
from thinking_dataset.config.config_keys import ConfigKeys as CK
import thinking_dataset.config as conf
from thinking_dataset.io.virtual_files import VirtualFiles


class GetFileList(Operation):
    """
    A class to retrieve a list of virtual files in the dataset.
    """

    def execute(self):
        try:
            dataset_type = conf.get_value(CK.DATASET_TYPE)
            dataset_info = self.data_tonic.get_info.execute(
                f"{self.data_tonic.organization}/{self.data_tonic.dataset}")

            virtual_files = VirtualFiles()
            for file in dataset_info.siblings:
                if file.rfilename.endswith(f'.{dataset_type}'):
                    virtual_files.add_file(file.rfilename, file.size,
                                           file.lastModified)

            Log.info(f"Dataset files: {virtual_files.get_files()}")
            return virtual_files
        except Exception as e:
            raise RuntimeError(f"Error retrieving file list: {e}")
