import logging
import os
import time

def log_message(message, console_output=True, file_logger=None, test_mode=False, console_logger=None):
    """
    Log a message to both file and console loggers.
    
    Args:
        message: Message to log
        console_output: Whether to log to console (default: True)
        file_logger: File logger instance
        test_mode: Whether in test mode
        console_logger: Console logger instance
    """
    if file_logger and not test_mode:
        file_logger.info(message)
    
    if console_output and console_logger:
        try:
            console_logger.info(message)
        except UnicodeEncodeError:
            console_logger.info(message.encode('ascii', errors='replace').decode('ascii'))

def setup_loggers(log_path, test_mode=False):
    """
    Set up console and file loggers.
    
    Args:
        log_path: Path to save log files
        test_mode: Whether in test mode
        
    Returns:
        tuple: (console_logger, file_logger)
    """
    if test_mode:
        console_logger = logging.getLogger("console")
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
        console_logger.addHandler(handler)
        console_logger.setLevel(logging.INFO)
        console_logger.propagate = False
        return console_logger, None
    
    os.makedirs(log_path, exist_ok=True)
    console_logger, file_logger = logging.getLogger("console"), logging.getLogger("file")
    
    # Console logger setup
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
    console_logger.addHandler(console_handler)
    console_logger.setLevel(logging.INFO)
    console_logger.propagate = False
    
    # File logger setup
    log_file = os.path.join(log_path, f"reason_{int(time.time())}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%X"))
    file_logger.addHandler(file_handler)
    file_logger.setLevel(logging.INFO)
    file_logger.propagate = False
    
    return console_logger, file_logger
