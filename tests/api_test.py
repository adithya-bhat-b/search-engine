#
# Copyright (c) 2020. Unibuddy, Inc. All Rights Reserved.
#
# Author: adithya.bhat@gmail.com (Adithya bhat)
#
# This test script is used to the test the API functionality to
# get the relevant summaries for the list of queries
# Loads the queries and results from INP_FILE and tests the results
# against the API response
# Please start the server before running the script
# To run the testcase
# python tests/api_test.py

import unittest
from json import dumps
from os import path

import requests

from utilities.json_parser import load_json

INP_FILE = "api-test-inputs.json"
FILE_DIR = "data" 
SERVER_IP = "127.0.0.1"
PORT = 8080
# url to check server status
SERVER_TEST_URL = "http://{0}:{1}/ping"
# API endpoint
SERVER_API_URL = "http://{0}:{1}/api/v1/get-matching-summaries"

def _get_api_results(queries, summary_num):
    """
    Function to get the API response from the input queries
    """
    url = SERVER_API_URL.format(SERVER_IP, PORT)
    data = {
        "queries": queries,
        "K": summary_num
    }
    res = requests.post(url, data=dumps(data))
    return res.json()

def _load_test_json():
    """
    Function to load the test inputs and response to be tested
    """
    inp_json_file_path = path.join(path.dirname(__file__),
                                   FILE_DIR, INP_FILE)   
    res, err, trace = load_json(inp_json_file_path)
    if not err:
        return res
    raise Exception("Unable to load the json file: %s, Error: %s, Trace:%s"
                    % (inp_json_file_path, err, trace))

def _create_cases(cases, positive=True):
    """
    Function used to create dynamic positive and negative test cases 
    based on input in json data
    """
    if positive:
        method_name = 'test_positive_case_{0}'
        compare_method = lambda queries, num, results: lambda self: self.assertDictEqual(
                                                                  _get_api_results(queries, num), 
                                                                  results)
    else:
        method_name = 'test_negative_case_{0}'
        compare_method = lambda queries, num, results: lambda self: self.assertNotEqual(
                                                                  _get_api_results(queries, num), 
                                                                  results)
    for i in range(len(cases)):
        current_tc = cases[i]
        testmethodname = method_name.format(i)
        setattr(ValidateAPIServer, testmethodname, 
                compare_method(current_tc["queries"], current_tc["summary_num"],
                               current_tc["results"]))

class ValidateAPIServer(unittest.TestCase):
    def setUp(self):
        # Check the server status before test
        url = SERVER_TEST_URL.format(SERVER_IP, PORT)
        resp = requests.get(url)
        if resp.status_code != 200:
            raise Exception("Server http://%s:%s is not reachable." % (SERVER_IP, PORT)) 

if __name__ == "__main__":
    io_data = _load_test_json()
    _create_cases(io_data["positive_cases"])
    _create_cases(io_data["negative_cases"], positive=False)
    unittest.main()