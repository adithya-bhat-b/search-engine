#
# Copyright (c) 2020. Unibuddy, Inc. All Rights Reserved.
#
# Author: adithya.bhat@gmail.com (Adithya bhat)
#
# This script exposes the rest endpoint to accept
# the requests and give search results
#
# Sample Usage 
# data = {
#    "queries": ["a is gift", "capitalism of selection "],
#    "K": 5
# }
# requests.post("http://127.0.0.1:8080/api/v1/get-matching-summaries", data=json.dumps(data))
# 
# To test the server status Use:
# request.get("http://127.0.0.1:8080/ping")
# To run the server:
# python src/server.py

import argparse
import json
from multiprocessing import cpu_count, Pool

import requests
from flask import Flask, request

from search.search_summary import Search
from src.config import Config
from utilities.json_parser import dump_json, load_json
from utilities.logger import create_logger

app = Flask(__name__)

logger = None

# json cache for http author requests
request_cache = None

def start_server():
    """
    Function used to start the http server using Flask
    """
    app.run(host = Config.HOSTNAME, port = Config.PORT)
    logger.info('Http Server is running at http://%s:%s' 
                % (Config.HOSTNAME, Config.PORT))

@app.route('/ping', methods=['GET'])
def ping():
    """
    Server test endpoint
    """
    res = {"status": "success"}
    return res

@app.route('/api/v1/get-matching-summaries', methods=['POST'])
def get_matching_summaries():
    """
    Function accepts http post request and calls Search-engine module to return the 
    search results
    Make http post request to the server with post data of the format:
    data = {
      "queries": ["a is gift", "capitalism of selection"],
      "K": 2
    }
    Returns:
      {
        "books": [
          [
            {
                "author": "Mark Manson",
                "id": 48,
                "query": "a is gift",
                "summary":"....."
            },
            {...}

          ], 
          [
            {
                "author": "Dan Harris",
                "id": 0,
                "query": "capitalism of selection",
                "summary": "....."
            },
            {...}
          ]
        ]
      }
    """
    request_data = json.loads(request.data)
    queries = request_data.get("queries", [])
    summary_limit = request_data.get("K", 0)
    logger.info("Recieved request for query-set: %s and no of summaries to retrieve "
                "based on the order of relevance is: %d" % (queries, summary_limit))
    # Get the output result
    output_res = get_matching_summaries_with_author(queries, summary_limit)
    # Update cache the author and book_id map
    _update_cache(request_cache)
    return {"books": output_res}

def get_matching_summaries_with_author(queries, summary_limit):
    """
    Function which takes list of queries and the no of summaries to return as
    the argument and returns search results
    Args:
      queries: list of queries
      summary_limit: no of summaries to return based on the relevance
    Returns:
      summaries_with_author: list of lists of the format
      [
          [
            {
                "author": "Mark Manson",
                "id": 48,
                "query": "a is gift",
                "summary":"....."
            },
            {...}

          ], 
          [
            {
                "author": "Dan Harris",
                "id": 0,
                "query": "capitalism of selection",
                "summary": "....."
            },
            {...}
          ]
        ]
    """
    # Get the summaries for all the queries
    summaries = _get_matching_summaries_for_queries(queries, summary_limit)
    #summaries = _multiprocess_requests(queries, summary_limit)
    # Get summaries with author info for each summary
    summaries_with_author = _get_author_and_summary_res(summaries)
    logger.info("Matching summaries with author info: %s." 
                % summaries_with_author)
    return summaries_with_author

def _update_cache(data):
    """
    Function which updates the author book map of request cache json
    """
    dump_json(Config.DATA_FILE_PATH, data)

def _get_matching_summaries_for_queries(queries, summary_limit):
    """
    Function which accepts the list of queries and no of summaries to return
    and get the the relevant summaries for individual queries from the search
    engine utility.
    Args:
      queries: list of queries
      summary_limit: no of summaries to return based on the relevance
    Returns:
      results: list of lists of query summaries
      [
          [
            {
                "id": 48,
                "query": "a is gift",
                "summary":"....."
            },
            {...}

          ], 
          [
            {
                "id": 0,
                "query": "capitalism of selection",
                "summary": "....."
            },
            {...}
          ]
        ]
    """
    results = []
    for query in queries:
        # getting list of summaries for individual query
        query_summaries = _make_search_summary_requests(query, summary_limit)
        results.append(query_summaries)
    return results

def _get_author_and_summary_res(all_summaries):
    """
    Function to get author info for each summary from the list of summaries
    Args:
      all_summaries: list of list of summaries
    Returns:
      all_summaries
      [
          [
            {
                "author": "Mark Manson",
                "id": 48,
                "query": "a is gift",
                "summary":"....."
            },
            {...}

          ], 
          [
            {
                "author": "Dan Harris",
                "id": 0,
                "query": "capitalism of selection",
                "summary": "....."
            },
            {...}
          ]
        ]
    """  
    for summary_set in all_summaries:
        for summary in summary_set:
          summary["author"] = _get_author_for_book(summary["id"])
    return all_summaries

def _make_search_summary_requests(query, summary_num):
    """
    This function calls the search engine module to get the relevant summaries

    """
    summaries = Search(query, summary_num, logger).get_query_search_results(query=query)
    logger.debug("The matching summaries for the query: %s are: %s"
                  % (query, summaries))
    return summaries


def _get_author_for_book(book_id):
    """
      This function gets the book_id and retuns the author
      either from cache or by making request to endpoint
    """
    req_body = {
      "book_id": book_id
    }
    logger.debug("Request URL: %s, request body: %s" 
                % (Config.AUTHOR_ENDPOINT, req_body))
    book_id_str = str(book_id)
    if book_id_str in request_cache:
        return request_cache[book_id_str]
    resp_body = requests.post(Config.AUTHOR_ENDPOINT, data=json.dumps(req_body))
    logger.debug("Response: %s" % resp_body)
    author = resp_body.json().get("author", None)
    if author:
        request_cache[book_id_str] = author
    return author

def _multiprocess_requests(queries, summary_limit):
    """
    Not in use
    Can be used for multiprocessing the requests
    """
    inputs_args = []
    for query in queries:
      inputs_args.append((query, summary_limit))
    with Pool(cpu_count()) as p:
      res = p.starmap(_make_search_summary_requests, inputs_args)
    return res

if __name__ == "__main__":
    # Initialize arg parser
    arg_parser = argparse.ArgumentParser("Load test cases into database.")
    arg_parser.add_argument("--debug",
                            help="run in debug mode (log at DEBUG level).",
                            action="store_true")
    args = arg_parser.parse_args()
    # If the server is running in debug mode log level is debug else info
    log_level = "debug" if args.debug else "info"
    # Create logger
    logger = create_logger(Config.LOG_DIR, Config.LOG_FILE, log_level)
    # Get http request cache for authors from the json cache file
    request_cache, _, _ = load_json(Config.DATA_FILE_PATH)
    start_server()