# Search engine
Utility for search engine

### Directory Structure
At any time you should ensure that your repo has the following top level directory:
  1. `/search`: It has the module for search utility
  It has a directory called `data` which has the input json and cache json files.
  It also has `config.py` which carries the configuration info.
  2. `/src`: This has the server and its corresponding configuration.
  It also constitutes `data` directory to have request cache. 
  3. `/tests`: This directory consists of tests and test input data.
  4. `/utilities`: This file contains the utilities like load and dump jsons and
  create loggers
  5. `/logs`: Optional logs directory, logs can be configures anywhere of one's choice
  6. `requirements.txt`: It has all the packages to be installed
  7. `setup.py`: Script to setup the project
  8. `LICENSE`: License information

### Build
1. To install the dependancies run:
    #### python setup.py develop

2. To run the server:
    #### python src/server.py

3. To run the tests:
    #### python tests/{test_name}.py

