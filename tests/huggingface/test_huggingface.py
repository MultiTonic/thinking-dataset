import os
import pytest
from unittest.mock import patch, MagicMock
from huggingface_hub import HfApi, DatasetInfo
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
HF_ORGANIZATION = "DataTonic"
HF_DATASET = "cablegate-pdf-dataset"  # Specify the dataset name

def test_hf_connection():
    with patch.object(HfApi, 'whoami', return_value={'name': 'p3nGu1nZz'}):
        api = HfApi(token=HF_TOKEN)
        hf_info = api.whoami()
        logger.info(f"Connected to Hugging Face as: {hf_info['name']}")
        assert hf_info is not None
        assert "name" in hf_info

def test_list_datatonic_datasets():
    mock_datasets = [{'id': 'DataTonic/cablegate-pdf-dataset'}]
    with patch.object(HfApi, 'list_datasets', return_value=mock_datasets):
        api = HfApi(token=HF_TOKEN)
        datasets = list(api.list_datasets(author=HF_ORGANIZATION))
        logger.info(f"Number of DataTonic datasets listed: {len(datasets)}")
        assert datasets is not None
        assert len(datasets) > 0

def test_dataset_metadata_attributes():
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", private=False, downloads=34,
        last_modified=None, tags=['cleaned-text']
    )
    with patch.object(HfApi, 'dataset_info', return_value=mock_dataset_info):
        api = HfApi(token=HF_TOKEN)
        dataset_info = api.dataset_info(f"{HF_ORGANIZATION}/{HF_DATASET}")
        logger.info(f"Dataset metadata: {dataset_info}")
        assert dataset_info is not None
        assert hasattr(dataset_info, "id")
        assert hasattr(dataset_info, "private")
        assert hasattr(dataset_info, "downloads")
        assert hasattr(dataset_info, "last_modified")
        assert hasattr(dataset_info, "tags")

def test_search_datasets():
    mock_search_results = [{'id': f"{HF_ORGANIZATION}/{HF_DATASET}"}]
    with patch.object(HfApi, 'list_datasets', return_value=mock_search_results):
        api = HfApi(token=HF_TOKEN)
        search_results = list(api.list_datasets(search=f"{HF_DATASET}"))
        logger.info(f"Search results for '{HF_DATASET}': {len(search_results)}")
        assert search_results is not None
        assert len(search_results) > 0

def test_dataset_tags():
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", tags=['cleaned-text']
    )
    with patch.object(HfApi, 'dataset_info', return_value=mock_dataset_info):
        api = HfApi(token=HF_TOKEN)
        dataset_info = api.dataset_info(f"{HF_ORGANIZATION}/{HF_DATASET}")
        logger.info(f"Dataset tags: {dataset_info.tags}")
        assert "cleaned-text" in dataset_info.tags

def test_dataset_card_content():
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", card_data={'pretty_name': 'Cable Gate (Cleaned)', 'language': ['en']}
    )
    with patch.object(HfApi, 'dataset_info', return_value=mock_dataset_info):
        api = HfApi(token=HF_TOKEN)
        dataset_info = api.dataset_info(f"{HF_ORGANIZATION}/{HF_DATASET}")
        logger.info(f"Dataset card data: {dataset_info.card_data}")
        assert "pretty_name" in dataset_info.card_data
        assert "language" in dataset_info.card_data

def test_dataset_download_url():
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", siblings=[MagicMock(rfilename='file.parquet')]
    )
    with patch.object(HfApi, 'dataset_info', return_value=mock_dataset_info):
        api = HfApi(token=HF_TOKEN)
        dataset_info = api.dataset_info(f"{HF_ORGANIZATION}/{HF_DATASET}")
        download_urls = [file.rfilename for file in dataset_info.siblings if file.rfilename.endswith('.parquet')]
        logger.info(f"Dataset download URLs: {download_urls}")
        assert len(download_urls) > 0

def test_dataset_permissions():
    mock_dataset_info = DatasetInfo(id=f"{HF_ORGANIZATION}/{HF_DATASET}", private=False)
    with patch.object(HfApi, 'dataset_info', return_value=mock_dataset_info):
        api = HfApi(token=HF_TOKEN)
        dataset_info = api.dataset_info(f"{HF_ORGANIZATION}/{HF_DATASET}")
        logger.info(f"Dataset permissions: {dataset_info.private}")
        assert dataset_info.private == False

def test_dataset_file_list():
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", siblings=[MagicMock(rfilename='README.md')]
    )
    with patch.object(HfApi, 'dataset_info', return_value=mock_dataset_info):
        api = HfApi(token=HF_TOKEN)
        dataset_info = api.dataset_info(f"{HF_ORGANIZATION}/{HF_DATASET}")
        file_list = dataset_info.siblings
        logger.info(f"Dataset files: {file_list}")
        assert len(file_list) > 0

def test_dataset_download_size():
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", card_data={'download_size': 229353983}
    )
    with patch.object(HfApi, 'dataset_info', return_value=mock_dataset_info):
        api = HfApi(token=HF_TOKEN)
        dataset_info = api.dataset_info(f"{HF_ORGANIZATION}/{HF_DATASET}")
        download_size = dataset_info.card_data.get('download_size', 0)
        logger.info(f"Dataset download size: {download_size}")
        assert download_size == 229353983

def test_dataset_configurations():
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", card_data={'configs': [{'config_name': 'default'}]}
    )
    with patch.object(HfApi, 'dataset_info', return_value=mock_dataset_info):
        api = HfApi(token=HF_TOKEN)
        dataset_info = api.dataset_info(f"{HF_ORGANIZATION}/{HF_DATASET}")
        configs = dataset_info.card_data.get('configs', [])
        logger.info(f"Dataset configurations: {configs}")
        assert len(configs) > 0
        assert configs[0]['config_name'] == 'default'

def test_dataset_description():
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", card_data={'description': 'Sample description'}
    )
    with patch.object(HfApi, 'dataset_info', return_value=mock_dataset_info):
        api = HfApi(token=HF_TOKEN)
        dataset_info = api.dataset_info(f"{HF_ORGANIZATION}/{HF_DATASET}")
        description = dataset_info.card_data.get('description', '')
        logger.info(f"Dataset description: {description}")
        assert len(description) > 0

def test_dataset_license():
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", card_data={'license': 'MIT'}
    )
    with patch.object(HfApi, 'dataset_info', return_value=mock_dataset_info):
        api = HfApi(token=HF_TOKEN)
        dataset_info = api.dataset_info(f"{HF_ORGANIZATION}/{HF_DATASET}")
        license_info = dataset_info.card_data.get('license', None)
        logger.info(f"Dataset license: {license_info}")
        assert license_info is not None

def test_dataset_split_information():
    mock_dataset_info = DatasetInfo(
        id=f"{HF_ORGANIZATION}/{HF_DATASET}", card_data={'dataset_info': {'splits': [{'name': 'train'}]}}
    )
    with patch.object(HfApi, 'dataset_info', return_value=mock_dataset_info):
        api = HfApi(token=HF_TOKEN)
        dataset_info = api.dataset_info(f"{HF_ORGANIZATION}/{HF_DATASET}")
        splits = dataset_info.card_data['dataset_info']['splits']
        logger.info(f"Dataset splits: {splits}")
        assert len(splits) > 0
        assert splits[0]['name'] == 'train'

if __name__ == "__main__":
    pytest.main()
