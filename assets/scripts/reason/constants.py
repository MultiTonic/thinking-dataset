"""
Constants used throughout the reasoning dataset project.
"""

# Processing parameters
MAX_WORKERS = 15
TEST_TIMEOUT = 30
CHECKPOINT_INTERVAL = 1000
BATCH_SIZE = 100
MAX_RETRIES = 5
REQUEST_TIMEOUT = 600
ENDPOINT_COOLDOWN = 30

# Default categories
DEFAULT_CATEGORIES = ["dark_thoughts", "benign"]

# File system
DEFAULT_LOG_DIR = "logs"
DEFAULT_OUTPUT_DIR = None  # Will default to current working directory

# API parameters
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 1
DEFAULT_TOP_P = 0.95
DEFAULT_MIN_LENGTH = 512
