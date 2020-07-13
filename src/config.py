from os import path

class Config:
      
    # HTTP server constants
    HOSTNAME = "0.0.0.0"
    PORT = 8080

    # Logging Constants
    LOG_DIR = path.join(path.dirname(path.dirname(__file__)), "logs")
    LOG_FILE = "search_engine.log"

    # Http chache json file
    DATA_FILE_PATH = path.join(path.dirname(__file__),
                               "data", 
                               "request_cache.json")

    # Endpoint to get Author for book
    AUTHOR_ENDPOINT = "https://ie4djxzt8j.execute-api.eu-west-1.amazonaws.com/coding"