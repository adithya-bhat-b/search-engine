from os import path

class Config:
    # Cache file name
    CACHE_FILE = "cache.json"
    # Data directory for cache and input json files
    DATA_DIR = "data"
    # Input json file
    INPUT_FILE = "input.json"
    # Log directory
    LOG_DIR = path.join(path.dirname(path.dirname(__file__)), "logs")
    # Log file name
    LOG_FILE = "search_engine.log"