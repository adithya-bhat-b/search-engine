#
# Copyright (c) 2020. Unibuddy, Inc. All Rights Reserved.
#
# Author: adithya.bhat@gmail.com (Adithya bhat)
#
# This function is used to create the logger
# accepts log-dir and log_file and returns the logger object 
# based on the logger level passed
# Usage
# logger = create_logger("C:/Dev", "test.log", level="error")

import logging
from logging.handlers import RotatingFileHandler
from os import path

def create_logger(log_dir, log_file, level="info"):
    """
    Function used to create logger object based on log directory
    and log file name
    """
    handler = RotatingFileHandler(filename=path.join(log_dir, log_file),
                                  mode='a', maxBytes=5000000, backupCount=10)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s, %(lineno)d [%(name)s]: %(message)s', '%d-%b-%y %H:%M:%S')
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    log_level = _get_log_level(level)
    logger.setLevel(log_level)
    logger.addHandler(handler)
    return logger

def _get_log_level(level):
    """
    Returns the log level object based on the input
    """
    level = level.lower()
    logging_level = logging.DEBUG
    if level == "info":
        logging_level = logging.INFO
    elif level == "warning":
        logging_level = logging.WARNING
    elif level == "error":
        logging_level = logging.ERROR
    elif level == "critical":
        logging_level = logging.CRITICAL
    return logging_level