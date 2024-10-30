# ./scripts/utilities/easylog.py

import logging
import locale
import io
import sys
import warnings
import subprocess

class EasyLogger:
    def __init__(self):
        self._set_utf8_encoding()
        self._configure_logging()

    def _check_numpy_version(self):
        import numpy as np
        # Suppress numpy-related warnings
        warnings.filterwarnings('ignore', category=UserWarning, module='numpy')
        
        if np.__version__.startswith('2'):
            print("Detected NumPy 2.x. Downgrading to compatible version...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy<2.0.0", "--force-reinstall"])
            print("NumPy downgrade complete. Please restart the application.")
            sys.exit(0)

    def _set_utf8_encoding(self):
        # Force UTF-8 for Windows
        if sys.platform.startswith('win'):
            try:
                locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            except locale.Error:
                locale.setlocale(locale.LC_ALL, '')
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    def _configure_logging(self):
        # Create a custom formatter that handles UTF-8
        class UTF8Formatter(logging.Formatter):
            def __init__(self, fmt=None, datefmt=None):
                super().__init__(fmt, datefmt)

            def format(self, record):
                if isinstance(record.msg, bytes):
                    record.msg = record.msg.decode('utf-8', errors='replace')
                return super().format(record)

        # Configure logging
        formatter = UTF8Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)

        logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
        logging.getLogger().handlers = [handler]

    def initialize(self):
        self._check_numpy_version()