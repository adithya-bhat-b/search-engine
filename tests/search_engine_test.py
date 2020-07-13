#
# Copyright (c) 2020. Unibuddy, Inc. All Rights Reserved.
#
# Author: adithya.bhat@gmail.com (Adithya bhat)
#
# This test script is used to the test the search enginemodule to
# get the relevant summaries for a query.
# Loads the queries and results from INP_FILE and tests the results
# against the API response.
# To run the testcase
# python tests/search-engine_test.py


import unittest
from json import load
from os import path

from search.search_summary import Search
from utilities.json_parser import load_json

INP_FILE = "search-engine-test-inputs.json"
FILE_DIR = "data" 

def _get_search_results(query, summary_num):
    """
    Function to make requests to search-engine module and retrieve the response
    """
    res = Search(query, summary_num).get_query_search_results()
    return res

def _load_test_json():
    """
    Function to load the the set of inputs to be tested from the 
    input json file
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
        compare_method = lambda query, num, results: lambda self: self.assertListEqual(
                                                                  _get_search_results(query, num), 
                                                                  results)
    else:
        method_name = 'test_negative_case_{0}'
        compare_method = lambda query, num, results: lambda self: self.assertNotEqual(
                                                                  _get_search_results(query, num), 
                                                                  results)
    for i in range(len(cases)):
        current_tc = cases[i]
        testmethodname = method_name.format(i)
        setattr(ValidateSearchEngine, testmethodname, 
                compare_method(current_tc["query"], current_tc["summary_num"],
                               current_tc["results"]))

class ValidateSearchEngine(unittest.TestCase):
    pass

if __name__ == "__main__":
    io_data = _load_test_json()
    _create_cases(io_data["positive_cases"])
    _create_cases(io_data["negative_cases"], positive=False)
    unittest.main()