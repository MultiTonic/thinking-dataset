# @file thinking_dataset/datasets/operations/get_download_urls.py
# @description Operation to retrieve dataset download URLs.
# @version 1.0.0
# @license MIT

from .operation import Operation
from ...utilities.log import Log
from ...config.config import Config
from ...config.config_keys import ConfigKeys as Keys


class GetDownloadUrls(Operation):
    """
    Operation class to retrieve dataset download URLs.
    """

    def execute(self, dataset_id):
        try:
            dataset_info = self.data_tonic.get_info.execute(dataset_id)
            dataset_type = Config.get_value(Keys.DATASET_TYPE)
            download_urls = [
                file.rfilename for file in dataset_info.siblings
                if file.rfilename.endswith(f'.{dataset_type}')
            ]
            Log.info(f"Dataset download URLs: {download_urls}")
            return download_urls
        except Exception as e:
            Log.error(f"Error retrieving download URLs for {dataset_id}: {e}")
            raise e
