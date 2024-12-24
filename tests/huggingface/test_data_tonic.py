import os
import pytest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from loguru import logger
from huggingface_hub import DatasetInfo

# Use relative imports
from thinking_dataset.connector import Connector
from thinking_dataset.data_tonic import DataTonic

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
HF_ORGANIZATION = "DataTonic"
HF_DATASET = "cablegate-pdf-dataset"
HF_USER = os.getenv("HF_USER")


def test_hf_connection():
    connector = Connector(token=HF_TOKEN)
    with patch.object(connector.api, 'whoami', return_value={'name': HF_USER}):
        hf_info = connector.get_whoami()
        logger.info(f"Connected to Hugging Face as: {hf_info['name']}")
        assert hf_info is not None
        assert "name" in hf_info


def test_list_datatonic_datasets():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_datasets_id = f"{HF_ORGANIZATION}/{HF_DATASET}"
    mock_datasets = [{'id': mock_datasets_id}]
    with patch.object(client.api, 'list_datasets', return_value=mock_datasets):
        datasets = client.list_organization_datasets()
        logger.info(f"Number of DataTonic datasets listed: {len(datasets)}")
        assert datasets is not None
        assert len(datasets) > 0


def test_dataset_metadata_attributes():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", private=False, downloads=34,
        last_modified=None, tags=['cleaned-text']
    )
    with patch.object(client.api, 'dataset_info',
                      return_value=mock_dataset_info):
        dataset_info = client.get_dataset_metadata()
        logger.info(f"Dataset metadata: {dataset_info}")
        assert dataset_info is not None
        assert hasattr(dataset_info, "id")
        assert hasattr(dataset_info, "private")
        assert hasattr(dataset_info, "downloads")
        assert hasattr(dataset_info, "last_modified")
        assert hasattr(dataset_info, "tags")


def test_search_datasets():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_search_results_id = f"{HF_ORGANIZATION}/{HF_DATASET}"
    mock_search_results = [{'id': mock_search_results_id}]
    with patch.object(client.api, 'list_datasets',
                      return_value=mock_search_results):
        search_results = client.list_datasets(search=HF_DATASET)
        logger.info(
            f"Search results for '{HF_DATASET}': {len(search_results)}"
        )
        assert search_results is not None
        assert len(search_results) > 0


def test_dataset_tags():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", tags=['cleaned-text']
    )
    with patch.object(client.api, 'dataset_info',
                      return_value=mock_dataset_info):
        tags = client.get_dataset_tags()
        logger.info(f"Dataset tags: {tags}")
        assert "cleaned-text" in tags


def test_dataset_card_content():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        card_data={'pretty_name': 'Cable Gate (Cleaned)', 'language': ['en']}
    )
    with patch.object(client.api, 'dataset_info',
                      return_value=mock_dataset_info):
        card_content = client.get_dataset_card_content()
        logger.info(f"Dataset card data: {card_content}")
        assert "pretty_name" in card_content
        assert "language" in card_content


def test_dataset_download_url():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        siblings=[MagicMock(rfilename='file.parquet')]
    )
    with patch.object(client.api, 'dataset_info',
                      return_value=mock_dataset_info):
        download_urls = client.get_dataset_download_urls()
        logger.info(f"Dataset download URLs: {download_urls}")
        assert len(download_urls) > 0


def test_dataset_permissions():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(id=f"{HF_ORGANIZATION}/{HF_DATASET}",
                                    private=False)
    with patch.object(client.api, 'dataset_info',
                      return_value=mock_dataset_info):
        permissions = client.get_dataset_permissions()
        logger.info(f"Dataset permissions: {permissions}")
        assert permissions is False


def test_dataset_file_list():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        siblings=[MagicMock(rfilename='README.md')]
    )
    with patch.object(client.api, 'dataset_info',
                      return_value=mock_dataset_info):
        file_list = client.get_dataset_file_list()
        logger.info(f"Dataset files: {file_list}")
        assert len(file_list) > 0


def test_dataset_download_size():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        card_data={'download_size': 229353983}
    )
    with patch.object(client.api, 'dataset_info',
                      return_value=mock_dataset_info):
        download_size = client.get_dataset_download_size()
        logger.info(f"Dataset download size: {download_size}")
        assert download_size == 229353983


def test_dataset_configurations():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        card_data={'configs': [{'config_name': 'default'}]}
    )
    with patch.object(client.api, 'dataset_info',
                      return_value=mock_dataset_info):
        configs = client.get_dataset_configurations()
        logger.info(f"Dataset configurations: {configs}")
        assert len(configs) > 0
        assert configs[0]['config_name'] == 'default'


def test_dataset_description():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        card_data={'description': 'Sample description'}
    )
    with patch.object(client.api, 'dataset_info',
                      return_value=mock_dataset_info):
        description = client.get_dataset_description()
        logger.info(f"Dataset description: {description}")
        assert len(description) > 0


def test_dataset_license():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        card_data={'license': 'MIT'}
    )
    with patch.object(client.api, 'dataset_info',
                      return_value=mock_dataset_info):
        license_info = client.get_dataset_license()
        logger.info(f"Dataset license: {license_info}")
        assert license_info is not None


def test_dataset_split_information():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        card_data={'dataset_info': {'splits': [{'name': 'train'}]}}
    )
    with patch.object(client.api, 'dataset_info',
                      return_value=mock_dataset_info):
        splits = client.get_dataset_split_information()
        logger.info(f"Dataset splits: {splits}")
        assert len(splits) > 0
        assert splits[0]['name'] == 'train'


if __name__ == "__main__":
    pytest.main()
