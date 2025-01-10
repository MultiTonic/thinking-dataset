# @file thinking_dataset/dataset/dataset_attributes.py
# @description Implementation of the DatasetAttributes class.
# @version 1.0.5
# @license MIT

import thinking_dataset.config.config_keys as Keys
import thinking_dataset.dataset.dataset_keys as DKeys
import thinking_dataset.config as conf
from thinking_dataset.utils.log import Log

CK = Keys.ConfigKeys
DK = DKeys.DatasetKeys


class DatasetAttributes:
    """
    A class to store dataset attributes.
    """

    def __init__(self):
        try:
            self.attributes = {
                DK.ORG: conf.get_env_value(CK.HF_ORG),
                DK.NAME: conf.get_value(CK.DATASET_NAME),
                DK.TYPE: conf.get_value(CK.DATASET_TYPE),
                DK.INCLUDE: conf.get_value(CK.INCLUDE_FILES),
                DK.EXCLUDE: conf.get_value(CK.EXCLUDE_FILES),
                DK.DATABASE: conf.get_value(CK.DATABASE_URL),
                DK.READ_TOKEN: conf.get_env_value(CK.HF_READ_TOKEN),
                DK.WRITE_TOKEN: conf.get_env_value(CK.HF_WRITE_TOKEN)
            }
            Log.info("DatasetAttributes initialized successfully!")
        except Exception as e:
            raise RuntimeError(f"Error initializing DatasetAttributes: {e}")
