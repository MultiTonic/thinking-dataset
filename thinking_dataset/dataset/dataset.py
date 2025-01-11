# @file thinking_dataset/dataset/dataset.py
# @description Implementation of the Dataset class.
# @version 1.0.18
# @license MIT

from typing import List, Optional
from thinking_dataset.db.database import Database
from thinking_dataset.tonics.data_tonic import DataTonic
from thinking_dataset.dataset.dataset_keys import DatasetKeys as DK
from thinking_dataset.dataset.dataset_operator import DatasetOperator as OP
from thinking_dataset.dataset.dataset_validator import DatasetValidator as Val
from thinking_dataset.dataset.dataset_attributes \
    import DatasetAttributes as Attr


class Dataset:
    """
    A class for dataset operations.
    """

    def __init__(self, data_tonic: DataTonic):
        if not data_tonic:
            raise ValueError("Data tonic is required.")

        try:
            self.api = data_tonic
            self.database = Database()
            attr = Attr().attributes
            Val.validate(attr)
            self.org = attr[DK.ORG]
            self.name = attr[DK.NAME]
            self.type = attr[DK.TYPE]
            self.include = attr[DK.INCLUDE]
            self.exclude = attr[DK.EXCLUDE]
            self.op = OP(self.api, attr, self.database)
        except Exception as e:
            raise RuntimeError(f"Error initializing Dataset: {e}")

    def download(self) -> bool:
        return self.op.download()

    def download_file(self, repo_id: str, filename: str, local_dir: str,
                      token: str):
        return self.op.download_file(repo_id, filename, local_dir, token)

    def get_card_content(self, *args, **kwargs):
        return self.op.get_card_content(*args, **kwargs)

    def get_configuration(self, *args, **kwargs):
        return self.op.get_configuration(*args, **kwargs)

    def get_description(self, *args, **kwargs):
        return self.op.get_description(*args, **kwargs)

    def get_download_size(self, *args, **kwargs):
        return self.op.get_download_size(*args, **kwargs)

    def get_download_urls(self, dataset_id: str):
        return self.op.get_download_urls(dataset_id)

    def get_file_list(self, *args, **kwargs):
        return self.op.get_file_list(*args, **kwargs)

    def get_info(self, *args, **kwargs):
        return self.op.get_info(*args, **kwargs)

    def get_license(self, *args, **kwargs):
        return self.op.get_license(*args, **kwargs)

    def get_metadata(self, *args, **kwargs):
        return self.op.get_metadata(*args, **kwargs)

    def get_permissions(self, *args, **kwargs):
        return self.op.get_permissions(*args, **kwargs)

    def get_split_information(self, *args, **kwargs):
        return self.op.get_split_information(*args, **kwargs)

    def get_tags(self, *args, **kwargs):
        return self.op.get_tags(*args, **kwargs)

    def get_whoami(self, *args, **kwargs):
        return self.op.get_whoami(*args, **kwargs)

    def list_datasets(self):
        return self.op.list_datasets()

    def load(self, files_to_load: Optional[List[str]] = None) -> bool:
        return self.op.load(files_to_load)
