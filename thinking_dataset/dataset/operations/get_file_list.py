# @file thinking_dataset/dataset/operations/get_file_list.py
# @description Operation to retrieve list of dataset remote files.
# @version 1.0.13
# @license MIT

import thinking_dataset.config as conf
import thinking_dataset.config.config_keys as Keys
import thinking_dataset.dataset.operations.operation as operation
import thinking_dataset.io.rfiles as rfiles

from thinking_dataset.utils.log import Log

CK = Keys.ConfigKeys


class GetFileList(operation.Operation):
    """
    A class to retrieve a list of remote files in the dataset.
    """

    def execute(self):
        try:
            dataset_type = conf.get_value(CK.DATASET_TYPE)
            org = conf.get_env_value(CK.HF_ORG)
            dataset_name = conf.get_value(CK.DATASET_NAME)

            Log.info(f"Dataset Type: {dataset_type}")
            Log.info(f"Organization: {org}")
            Log.info(f"Dataset Name: {dataset_name}")

            if not dataset_name:
                raise ValueError(
                    "Dataset name is not configured. "
                    "Please set the 'dataset.name' in your config.")

            dataset_info = self.data_tonic.get_info.execute(
                f"{org}/{dataset_name}")

            rfiles_obj = rfiles.RFiles()
            for file in dataset_info.siblings:
                if file.rfilename.endswith(f'.{dataset_type}'):
                    rfiles_obj.add_file(file.rfilename, file.size, "N/A")

            Log.info(f"Dataset files: {rfiles_obj.get_files()}")
            return rfiles_obj
        except Exception as e:
            Log.error(f"Error retrieving file list: {e}", exc_info=True)
            raise RuntimeError(f"Error retrieving file list: {e}")
