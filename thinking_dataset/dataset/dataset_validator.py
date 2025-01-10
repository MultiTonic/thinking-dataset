# @file thinking_dataset/validators/dataset_validator.py
# @description Implementation of the DatasetValidator class.
# @version 1.0.3
# @license MIT

from thinking_dataset.utils.log import Log
import thinking_dataset.dataset.dataset_keys as Keys

DK = Keys.DatasetKeys


class DatasetValidator:
    """
    A class for validating dataset configurations.
    """

    def __init__(self):
        Log.info("DatasetValidator initialized successfully!")

    @staticmethod
    def validate(attributes):
        if not attributes[DK.TYPE]:
            raise ValueError("Dataset type is not configured.")
        if not attributes[DK.NAME]:
            raise ValueError("Dataset name is not configured.")
        if not attributes[DK.ORG]:
            raise ValueError("Organization is not configured.")
        if not attributes[DK.DATABASE]:
            raise ValueError("Database URL is not configured.")
