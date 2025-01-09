# @file thinking_dataset/datasets/operations/get_download_urls.py
# @description Operation to retrieve dataset download URLs.
# @version 1.0.1
# @license MIT

from .operation import Operation
from ...utilities.log import Log
import thinking_dataset.config as cfg


class GetDownloadUrls(Operation):
    """
    Operation class to retrieve dataset download URLs.
    """

    def execute(self, dataset_id):
        try:
            dataset_info = self.data_tonic.get_info.execute(dataset_id)
            config_instance = cfg.initialize()
            dataset_type = config_instance.get_value(
                cfg.get_keys().DATASET_TYPE)
            download_urls = [
                file.rfilename for file in dataset_info.siblings
                if file.rfilename.endswith(f'.{dataset_type}')
            ]
            Log.info(f"Dataset download URLs: {download_urls}")
            return download_urls
        except Exception as e:
            Log.error(f"Error retrieving download URLs for {dataset_id}: {e}")
            raise e
