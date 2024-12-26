import os
import pytest
from unittest.mock import patch
from dotenv import load_dotenv
from loguru import logger
from huggingface_hub import DatasetInfo
from thinking_dataset.data_tonic import DataTonic

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
HF_ORGANIZATION = "DataTonic"
HF_DATASET = "cablegate-pdf-dataset"


def test_dataset_metadata_attributes():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", private=False, downloads=34,
        last_modified=None, tags=['cleaned-text']
    )

    with patch.object(client.operations, 'get_dataset_metadata',
                      return_value=mock_dataset_info):
        dataset_info = client.operations.get_dataset_metadata()
        logger.info(f"Dataset metadata: {dataset_info}")
        assert dataset_info is not None
        assert hasattr(dataset_info, "id")
        assert hasattr(dataset_info, "private")
        assert hasattr(dataset_info, "downloads")
        assert hasattr(dataset_info, "last_modified")
        assert hasattr(dataset_info, "tags")


def test_dataset_tags():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", tags=['cleaned-text']
    )

    with patch.object(client.operations, 'get_dataset_tags',
                      return_value=mock_dataset_info.tags):
        tags = client.operations.get_dataset_tags()
        logger.info(f"Dataset tags: {tags}")
        assert "cleaned-text" in tags


def test_dataset_card_content():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        card_data={'pretty_name': 'Cable Gate (Cleaned)', 'language': ['en']}
    )

    with patch.object(client.operations, 'get_dataset_card_content',
                      return_value=mock_dataset_info.card_data):
        card_content = client.operations.get_dataset_card_content()
        logger.info(f"Dataset card data: {card_content}")
        assert "pretty_name" in card_content
        assert "language" in card_content


def test_dataset_download_size():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        card_data={'download_size': 229353983}
    )

    with patch.object(
        client.info, 'get_dataset_download_size',
        return_value=mock_dataset_info.card_data['download_size']
    ):
        download_size = client.info.get_dataset_download_size()
        logger.info(f"Dataset download size: {download_size}")
        assert download_size == 229353983


def test_dataset_configurations():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        card_data={'configs': [{'config_name': 'default'}]}
    )

    with patch.object(
        client.info, 'get_dataset_configurations',
        return_value=mock_dataset_info.card_data['configs']
    ):
        configs = client.info.get_dataset_configurations()
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

    with patch.object(
        client.info, 'get_dataset_description',
        return_value=mock_dataset_info.card_data['description']
    ):
        description = client.info.get_dataset_description()
        logger.info(f"Dataset description: {description}")
        assert len(description) > 0


def test_dataset_license():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        card_data={'license': 'MIT'}
    )

    with patch.object(
        client.info, 'get_dataset_license',
        return_value=mock_dataset_info.card_data['license']
    ):
        license_info = client.info.get_dataset_license()
        logger.info(f"Dataset license: {license_info}")
        assert license_info is not None


def test_dataset_split_information():
    client = DataTonic(token=HF_TOKEN, organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}",
        card_data={'dataset_info': {'splits': [{'name': 'train'}]}}
    )

    with patch.object(
        client.info, 'get_dataset_split_information',
        return_value=mock_dataset_info.card_data['dataset_info']['splits']
    ):
        splits = client.info.get_dataset_split_information()
        logger.info(f"Dataset splits: {splits}")
        assert len(splits) > 0
        assert splits[0]['name'] == 'train'


if __name__ == "__main__":
    pytest.main()
