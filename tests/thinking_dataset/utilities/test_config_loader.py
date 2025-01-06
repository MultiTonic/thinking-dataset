"""
@file tests/thinking_dataset/utilities/test_config_loader.py
@description Unit tests for the ConfigLoader class.
@version 1.0.0
@license MIT
@see {@link https://github.com/MultiTonic/thinking-dataset|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|Hugging Face Organization}
"""

import pytest
import yaml
from unittest.mock import patch, mock_open
from thinking_dataset.config.config_loader import Loader


@pytest.fixture
def sample_yaml_content():
    return """
    database:
        host: localhost
        port: 5432
        user: test_user
        password: test_password
    """


def test_load_valid_config(sample_yaml_content):
    """
    Test loading a valid YAML configuration file.
    """
    with patch("builtins.open", mock_open(read_data=sample_yaml_content)):
        config_loader = Loader("fake_path.yaml")
        config = config_loader.get("database")

        assert config["host"] == "localhost"
        assert config["port"] == 5432
        assert config["user"] == "test_user"
        assert config["password"] == "test_password"


def test_file_not_found_error():
    """
    Test handling FileNotFoundError when the configuration file is not found.
    """
    with pytest.raises(FileNotFoundError):
        Loader("non_existent_file.yaml")


def test_yaml_parsing_error():
    """
    Test handling YAML parsing errors.
    """
    with patch("builtins.open", mock_open(read_data=":")):  # Invalid YAML
        with pytest.raises(yaml.YAMLError):
            Loader("fake_path.yaml")


def test_get_non_existent_section(sample_yaml_content):
    """
    Test retrieving a non-existent section from the configuration.
    """
    with patch("builtins.open", mock_open(read_data=sample_yaml_content)):
        config_loader = Loader("fake_path.yaml")
        config = config_loader.get("non_existent_section")

        assert config == {}


if __name__ == "__main__":
    pytest.main()
