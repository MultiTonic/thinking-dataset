# data_tonic.py

import os
from .connector import Connector

HF_ORGANIZATION = os.getenv("HF_ORGANIZATION")
HF_DATASET = os.getenv("HF_DATASET")
HF_DATASET_TYPE = os.getenv("HF_DATASET_TYPE", 'parquet')


class DataTonic(Connector):
    def __init__(
        self,
        token,
        organization=HF_ORGANIZATION,
        dataset=HF_DATASET
    ):
        super().__init__(token)
        self.organization = organization
        self.dataset = dataset

    def list_organization_datasets(self):
        datasets = self.list_datasets(author=self.organization)
        Connector.log_info(
            f"Number of {self.organization} datasets listed: {len(datasets)}"
        )
        return datasets

    def get_dataset_metadata(self):
        dataset_info = self.get_dataset_info(
            f"{self.organization}/{self.dataset}"
        )
        Connector.log_info(f"Dataset metadata: {dataset_info}")
        return dataset_info

    def get_dataset_tags(self):
        dataset_info = self.get_dataset_info(
            f"{self.organization}/{self.dataset}"
        )
        Connector.log_info(f"Dataset tags: {dataset_info.tags}")
        return dataset_info.tags

    def get_dataset_card_content(self):
        dataset_info = self.get_dataset_info(
            f"{self.organization}/{self.dataset}"
        )
        Connector.log_info(f"Dataset card data: {dataset_info.card_data}")
        return dataset_info.card_data

    def get_dataset_download_urls(self):
        dataset_info = self.get_dataset_info(
            f"{self.organization}/{self.dataset}"
        )
        download_urls = [
            file.rfilename
            for file in dataset_info.siblings
            if file.rfilename.endswith(f'.{HF_DATASET_TYPE}')
        ]
        Connector.log_info(f"Dataset download URLs: {download_urls}")
        return download_urls

    def get_dataset_permissions(self):
        dataset_info = self.get_dataset_info(
            f"{self.organization}/{self.dataset}"
        )
        Connector.log_info(f"Dataset permissions: {dataset_info.private}")
        return dataset_info.private

    def get_dataset_file_list(self):
        dataset_info = self.get_dataset_info(
            f"{self.organization}/{self.dataset}"
        )
        file_list = dataset_info.siblings
        Connector.log_info(f"Dataset files: {file_list}")
        return file_list

    def get_dataset_download_size(self):
        dataset_info = self.get_dataset_info(
            f"{self.organization}/{self.dataset}"
        )
        download_size = dataset_info.card_data.get('download_size', 0)
        Connector.log_info(f"Dataset download size: {download_size}")
        return download_size

    def get_dataset_configurations(self):
        dataset_info = self.get_dataset_info(
            f"{self.organization}/{self.dataset}"
        )
        configs = dataset_info.card_data.get('configs', [])
        Connector.log_info(f"Dataset configurations: {configs}")
        return configs

    def get_dataset_description(self):
        dataset_info = self.get_dataset_info(
            f"{self.organization}/{self.dataset}"
        )
        description = dataset_info.card_data.get('description', '')
        Connector.log_info(f"Dataset description: {description}")
        return description

    def get_dataset_license(self):
        dataset_info = self.get_dataset_info(
            f"{self.organization}/{self.dataset}"
        )
        license_info = dataset_info.card_data.get('license', None)
        Connector.log_info(f"Dataset license: {license_info}")
        return license_info

    def get_dataset_split_information(self):
        dataset_info = self.get_dataset_info(
            f"{self.organization}/{self.dataset}"
        )
        splits = dataset_info.card_data['dataset_info']['splits']
        Connector.log_info(f"Dataset splits: {splits}")
        return splits
