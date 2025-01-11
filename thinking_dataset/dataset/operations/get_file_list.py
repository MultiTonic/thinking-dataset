# @file thinking_dataset/dataset/operations/get_file_list.py
# @description Operation to retrieve list of dataset remote files.
# @version 1.0.19
# @license MIT

import thinking_dataset.config as conf
import thinking_dataset.config.config_keys as keys
import thinking_dataset.dataset.operations.operation as operation
import thinking_dataset.io.rfiles as rfiles
from thinking_dataset.utils.log import Log

CK = keys.ConfigKeys
OO = operation.Operation


class GetFileList(OO):
    """
    A class to retrieve a list of remote files in the dataset.
    """

    def execute(self):
        try:
            org = conf.get_env_value(CK.HF_ORG)
            name = conf.get_value(CK.DATASET_NAME)
            type = conf.get_value(CK.DATASET_TYPE)
            repo_id = f"{org}/{name}"

            Log.info(f"Repo Id: {repo_id}.{type}")

            if not name:
                raise ValueError(
                    "Dataset name is not configured. "
                    "Please set the 'dataset.name' in your config.")

            dataset_info = self.dt.api.repo_info(repo_id, repo_type="dataset")

            rfiles_obj = rfiles.RFiles()
            for file_info in dataset_info.siblings:
                if file_info.rfilename.endswith(f'.{type}'):
                    rfiles_obj.add_file(file_info.rfilename, file_info.size,
                                        "N/A")

            Log.info(f"Dataset files: {rfiles_obj.get_files()}")
            return rfiles_obj
        except Exception as e:
            Log.error(f"Error retrieving file list: {e}", exc_info=True)
            raise RuntimeError(f"Error retrieving file list: {e}")
