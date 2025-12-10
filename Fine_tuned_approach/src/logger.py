import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_file: str = "ats_pipeline.log", level=logging.INFO):
    """
    Setup a logger that writes to console and a rotating log file.
    """
    # Create a custom logger
    logger = logging.getLogger(name)
    
    # If logger already has handlers, remove them to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.setLevel(level)

    # Create handlers
    c_handler = logging.StreamHandler(sys.stdout)
    f_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)

    c_handler.setLevel(level)
    f_handler.setLevel(logging.DEBUG)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger
