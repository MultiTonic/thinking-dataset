import os
import pytest
from unittest.mock import patch
from dotenv import load_dotenv
from loguru import logger
from huggingface_hub import DatasetInfo
from thinking_dataset.tonics.data_tonic import DataTonic

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
HF_ORGANIZATION = "DataTonic"
HF_DATASET = "cablegate-pdf-dataset"


def test_list_datatonic_datasets():
    client = DataTonic(token=HF_TOKEN,
                       organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_datasets_id = f"{HF_ORGANIZATION}/{HF_DATASET}"
    mock_datasets = [{'id': mock_datasets_id}]

    with patch.object(client.operations,
                      'list_organization_datasets',
                      return_value=mock_datasets):
        datasets = client.operations.list_organization_datasets()
        logger.info(f"Number of DataTonic datasets listed: {len(datasets)}")
        assert datasets is not None
        assert len(datasets) > 0


def test_get_dataset_metadata():
    client = DataTonic(token=HF_TOKEN,
                       organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(id=f"{HF_ORGANIZATION}/{HF_DATASET}",
                                    private=False,
                                    downloads=34,
                                    last_modified=None,
                                    tags=['cleaned-text'])

    with patch.object(client.operations,
                      'get_dataset_metadata',
                      return_value=mock_dataset_info):
        dataset_info = client.operations.get_dataset_metadata()
        logger.info(f"Dataset metadata: {dataset_info}")
        assert dataset_info is not None
        assert hasattr(dataset_info, "id")
        assert hasattr(dataset_info, "private")
        assert hasattr(dataset_info, "downloads")
        assert hasattr(dataset_info, "last_modified")
        assert hasattr(dataset_info, "tags")


def test_get_dataset_tags():
    client = DataTonic(token=HF_TOKEN,
                       organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(id=f"{HF_ORGANIZATION}/{HF_DATASET}",
                                    tags=['cleaned-text'])

    with patch.object(client.operations,
                      'get_dataset_tags',
                      return_value=mock_dataset_info.tags):
        tags = client.operations.get_dataset_tags()
        logger.info(f"Dataset tags: {tags}")
        assert "cleaned-text" in tags


def test_get_dataset_card_content():
    client = DataTonic(token=HF_TOKEN,
                       organization=HF_ORGANIZATION,
                       dataset=HF_DATASET)
    mock_dataset_info = DatasetInfo(id=f"{HF_ORGANIZATION}/{HF_DATASET}",
                                    card_data={
                                        'pretty_name': 'Cable Gate (Cleaned)',
                                        'language': ['en']
                                    })

    with patch.object(client.operations,
                      'get_dataset_card_content',
                      return_value=mock_dataset_info.card_data):
        card_content = client.operations.get_dataset_card_content()
        logger.info(f"Dataset card data: {card_content}")
        assert "pretty_name" in card_content
        assert "language" in card_content


if __name__ == "__main__":
    pytest.main()
