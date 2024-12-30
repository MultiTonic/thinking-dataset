"""
@file tests/thinking_dataset/db/test_database_config.py
@description Unit tests for the DatabaseConfig class.
@version 1.0.0
@license MIT
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
from unittest.mock import patch
from thinking_dataset.db.database_config import DatabaseConfig


@pytest.fixture
def mock_config_data():
    return {
        'database': {
            'url': 'sqlite:///test.db',
            'type': 'sqlite',
            'pool_size': 10,
            'max_overflow': 20,
            'connect_timeout': 15,
            'read_timeout': 15,
            'log_queries': False,
            'environment': 'testing'  # Updated from 'test' to 'testing'
        }
    }


@pytest.fixture
def mock_config_data_defaults():
    return {
        'database': {
            'url': 'sqlite:///test.db'
            # Other config options are omitted to test default values
        }
    }


@pytest.fixture
def mock_config_data_invalid_types():
    return {
        'database': {
            'url': 'sqlite:///test.db',
            'pool_size': 'invalid_type',
            'max_overflow': 'invalid_type',
            'connect_timeout': 'invalid_type',
            'read_timeout': 'invalid_type'
        }
    }


@pytest.fixture
def mock_config_data_edge_cases():
    return {
        'database': {
            'url': 'sqlite:///test.db',
            'pool_size': 0,
            'max_overflow': 0,
            'connect_timeout': 0,
            'read_timeout': 0
        }
    }


@patch('thinking_dataset.db.database_config.ConfigLoader')
def test_database_config_instantiation(MockConfigLoader, mock_config_data):
    """
    Test the instantiation of DatabaseConfig.
    """
    # Mock the configuration loader to return our test configuration
    mock_loader_instance = MockConfigLoader.return_value
    mock_loader_instance.get.return_value = mock_config_data['database']

    # Test if the class instantiates without errors
    db_config = DatabaseConfig('mock_config_path')
    assert isinstance(db_config, DatabaseConfig)


@patch('thinking_dataset.db.database_config.ConfigLoader')
def test_database_config_validation(MockConfigLoader, mock_config_data):
    """
    Test the validation of DatabaseConfig settings.
    """
    # Mock the configuration loader to return our test configuration
    mock_loader_instance = MockConfigLoader.return_value
    mock_loader_instance.get.return_value = mock_config_data['database']

    # Initialize DatabaseConfig with the mocked config path
    db_config = DatabaseConfig('mock_config_path')

    # Test validation passes with valid config
    db_config.validate()

    # Test validation fails with invalid config
    mock_config_data['database']['url'] = ''
    mock_loader_instance.get.return_value = mock_config_data['database']
    db_config = DatabaseConfig('mock_config_path')
    with pytest.raises(ValueError, match="Database URL must be set."):
        db_config.validate()


@patch('thinking_dataset.db.database_config.ConfigLoader')
def test_database_config_defaults(MockConfigLoader, mock_config_data_defaults):
    """
    Test the default values of DatabaseConfig.
    """
    # Mock the configuration loader to return our test configuration
    mock_loader_instance = MockConfigLoader.return_value
    mock_loader_instance.get.return_value = mock_config_data_defaults[
        'database']

    # Initialize DatabaseConfig with the mocked config path
    db_config = DatabaseConfig('mock_config_path')

    # Assert default values are set correctly
    assert db_config.database_type == 'sqlite'
    assert db_config.pool_size == 5
    assert db_config.max_overflow == 10
    assert db_config.connect_timeout == 30
    assert db_config.read_timeout == 30
    assert db_config.log_queries is True
    assert db_config.environment == 'development'


@patch('thinking_dataset.db.database_config.ConfigLoader')
def test_database_config_invalid_types(MockConfigLoader,
                                       mock_config_data_invalid_types):
    """
    Test invalid data types in DatabaseConfig.
    """
    # Mock the configuration loader to return our test configuration
    mock_loader_instance = MockConfigLoader.return_value
    mock_loader_instance.get.return_value = mock_config_data_invalid_types[
        'database']

    # Initialize DatabaseConfig with the mocked config path
    db_config = DatabaseConfig('mock_config_path')

    # Test validation raises errors for invalid types
    with pytest.raises(ValueError,
                       match="Pool size must be a non-negative integer."):
        db_config.validate()

    mock_config_data_invalid_types['database']['pool_size'] = 10
    mock_loader_instance.get.return_value = mock_config_data_invalid_types[
        'database']
    db_config = DatabaseConfig('mock_config_path')
    with pytest.raises(ValueError,
                       match="Max overflow must be a non-negative integer."):
        db_config.validate()

    mock_config_data_invalid_types['database']['max_overflow'] = 10
    mock_loader_instance.get.return_value = mock_config_data_invalid_types[
        'database']
    db_config = DatabaseConfig('mock_config_path')
    with pytest.raises(
            ValueError,
            match="Connect timeout must be a non-negative integer."):
        db_config.validate()

    mock_config_data_invalid_types['database']['connect_timeout'] = 10
    mock_loader_instance.get.return_value = mock_config_data_invalid_types[
        'database']
    db_config = DatabaseConfig('mock_config_path')
    with pytest.raises(ValueError,
                       match="Read timeout must be a non-negative integer."):
        db_config.validate()


@patch('thinking_dataset.db.database_config.ConfigLoader')
def test_database_config_edge_cases(MockConfigLoader,
                                    mock_config_data_edge_cases):
    """
    Test edge case values in DatabaseConfig.
    """
    # Mock the configuration loader to return our test configuration
    mock_loader_instance = MockConfigLoader.return_value
    mock_loader_instance.get.return_value = mock_config_data_edge_cases[
        'database']

    # Initialize DatabaseConfig with the mocked config path
    db_config = DatabaseConfig('mock_config_path')

    # Test validation passes with edge case values
    db_config.validate()

    # Assert edge case values are set correctly
    assert db_config.pool_size == 0
    assert db_config.max_overflow == 0
    assert db_config.connect_timeout == 0
    assert db_config.read_timeout == 0


if __name__ == '__main__':
    pytest.main()
