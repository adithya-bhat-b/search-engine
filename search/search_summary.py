#
# Copyright (c) 2020. Unibuddy, Inc. All Rights Reserved.
#
# Author: adithya.bhat@gmail.com (Adithya bhat)
#
# This module is used to get the relevant summaries for
# the given query with the search limit.
#
# Sample Usage 
# query = "is your problems"
# summary_num = 3
# res = Search(query, summary_num).get_query_search_results()
# res is of the format:
#  [
#   {
#        "id": 48,
#        "summary":"....."
#    },
#    {
#        "id": 12,
#        "summary":"....."
#    },
#    {
#        "id": 25,
#        "summary":"....."
#    },
#  ]

from os import path

from search.config import Config
from utilities.json_parser import dump_json, load_json
from utilities.logger import create_logger

class Search:
    """
    Class which is used to get limited the relevant sumarries with thier id 
    for the given query
    query = "is your problems"
    summary_num = 3
    result = 
      [
            {
                "id": 48,
                "summary":"....."
            },
            {
                "id": 12,
                "summary":"....."
            },
            {
                "id": 25,
                "summary":"....."
            },
        ]
    """
    # Data from input.json
    INPUT_DATA = {}
    SUMMARIES_KEY = "summaries"
    SUMMARY_KEY = "summary"

    def __init__(self, query: str, summary_num: int, logger=None):
        self.logger = logger
        if not logger:
            self.logger = create_logger(Config.LOG_DIR, Config.LOG_FILE)
        self.logger.info("Query: '%s', No of summaries to return: %d"
                         % (query, summary_num))
        self.query = query.lower()
        self.summary_num = summary_num

    def _load_json_for_keys(self, file: str, *keys: list, directory: str="") -> dict:
        """
        Function load the json file and returns the result for specified keys
        Args:
            file: json file name
            directory: json file directory
            keys: list of keys to be filtered in the loaded json
        Returns:
            json_out: json output having only *keys
        """
        file_path = path.join(path.dirname(__file__), directory, file)
        # Get the json data with error if any
        json_out, err, trace = load_json(file_path)
        if not err:
            # Filtering the json output for only specific keys
            filtered_json = dict((key, json_out[key]) for key in keys if key in json_out)
            self.logger.debug("Loaded json for filtered keys is: %s" % filtered_json)
            return filtered_json
        self.logger.error("Error while loading the json file:%s , Error:%s, Trace: %s"
                          % (file, err, trace))
        return json_out

    def get_query_search_results(self, **custom_dict: dict):
        """
        This is the main function used to return the relevant summaries with
        their ids for the given query
        Returns:
            summary_dict:
               result = 
                        [
                            {
                                "id": 48,
                                "summary":"....."
                            },
                            {
                                "id": 12,
                                "summary":"....."
                            },
                            {
                                "id": 25,
                                "summary":"....."
                            },
                        ]
        """
        # If there is not loaded input json data load it from the 
        # input json file
        if not self.INPUT_DATA:
            self.INPUT_DATA.update(
                self._load_json_for_keys(
                    Config.INPUT_FILE, 
                    self.SUMMARIES_KEY,
                    directory=Config.DATA_DIR))
        # Get the cached indexes of summaries in the order of relevance
        cache_data = self._load_json_for_keys(
                   Config.CACHE_FILE, 
                   self.query,
                   directory=Config.DATA_DIR)
        if cache_data:
            # If data is cached return it from the cache
            self.logger.debug("Cached data json with search query and relevant "
                              "summary indexes, data: %s" % cache_data)
            return self._get_limited_search_results(cache_data[self.query], custom_dict)
        # Get the matching score for each of the summary
        summary_match_scores = self._get_relevant_summaries()
        # Get the sorted summary indexes in desc order based the match
        sorted_summary_match_score = self._get_sorted_match_on_relevance(
                                   summary_match_scores)
        self.logger.debug("Sorted summary match scores: %s" 
                          % sorted_summary_match_score)
        # Update the cache with the map of summary index with desc order of
        # match and query
        self._update_cache(sorted_summary_match_score)
        # Get the top K matches
        summary_dict = self._get_limited_search_results(sorted_summary_match_score, 
                                                        custom_dict)
        self.logger.info("Matching output summary: %s" % summary_dict)
        return summary_dict

    def _update_cache(self, sorted_summary_match_score: list):
        """
        Update the result cache with the query and matching scores in desc 
        order of match
        Args:
            sorted_summary_match_score: sorted indexes of summaries in the
            desc order of match
            [2, 3, 1, 34, 15, ...]
        """
        cache_file = path.join(path.dirname(__file__), Config.DATA_DIR, 
                               Config.CACHE_FILE)
        cache_dict, err, trace = load_json(cache_file)
        if not err:
            # If no error update the cache json data
            cache_dict.update({
                self.query: sorted_summary_match_score
            })
            # Dump the updated cache into file
            err, trace = dump_json(cache_file, cache_dict)
            if err:
                self.logger.error("Error dumping the data into cache file: %s,"
                                  "Error: %s, Trace: %s" 
                                  % (cache_file, err, trace))
            else:
                self.logger.info("Cache file: %s is updated successfully" % cache_file)
        else:
            self.logger.error("Error loading the cache file: %s, Error: %s, "
                              "Trace: %s" % (cache_file, err, trace))

    def _get_limited_search_results(self, data: list, custom_fields: dict={}) -> list: 
        """
        Function to get the top K search results from the input json with
        custom fields if required
        Args:
            data: list of summary indexes in the desc order of match for a query
            custom_fields: custom key-value pairs to be stored in the result array
        Returns:
            The array of summaries in desc order of match with the given query
            [
                {
                    "summary": "...",
                    "id": 23
                },
                {
                    "summary": "...",
                    "id": 45
                }
                {...}
            ]
        """
        return [
            {**self.INPUT_DATA[self.SUMMARIES_KEY][summary_index], **custom_fields}
            for summary_index in data[:self.summary_num]
        ]

    def _get_relevant_summaries(self) -> list:
        """
        Function to return the array of scores of summaries for the given array:
        Returns:
            Ex: [7, 5, 11, 23,..]
        """
        query_splits = self.query.split(" ")
        return [self._get_query_match_score(summary[self.SUMMARY_KEY], query_splits)
                for summary in self.INPUT_DATA[self.SUMMARIES_KEY]]

    @staticmethod
    def _get_query_match_score(summary: str, query_splits: list) -> int:
        """
        This is the function to get  the matching score for a summary with 
        the qiven query
        Args:
            summary: summary string
            query_splits: array of splitted queries
        Returns:
            query_count_in_summary: no of matches of the query in the given summary
        This method returns the total no of occurences of all the query words in the 
        summary.
        """
        summary_words = summary.lower().split(" ")
        query_count_in_summary = 0
        for qry in query_splits:
            query_count_in_summary += summary_words.count(qry)
        return query_count_in_summary

    @staticmethod
    def _get_sorted_match_on_relevance(data: list) -> list:
        """
        Function to sort the indexes in desc order of their value
        Ex:
         input = [7, 9, 2]
         output = [1, 0, 2]

        """
        return [i[0] for i in sorted(enumerate(data), key=lambda x: x[1], reverse=True) if i[1] != 0]




    