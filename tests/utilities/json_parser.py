#
# Copyright (c) 2020. Unibuddy, Inc. All Rights Reserved.
#
# Author: adithya.bhat@gmail.com (Adithya bhat)
#
# This function is used to load or dump json files
# loader loads the json file and returns the loaded json data
# dumper dumps the json data into the file
# Usage
# json_data = load_json("C:/Dev/test.json")
# dump_json("C:/Dev/test.json")

from json import dump, load
from os import path
from traceback import format_exc

def load_json(file_path: str):
    """
    Function to load a json file and return json data
    Args:
        file_path: file path
    Returns:
        loaded json data
    """
    if path.exists(file_path):
        try:
            with open(file_path, "rb") as fp:
                return (load(fp), None, None)
        except Exception as err:
            return ({}, err, format_exc())
    return ({}, "File doesn't exist", None)

def dump_json(file: str, data: dict, indent=4):
    """
    Function to dump the json data into the file
    Args:
        file: file path
        data: data to be dumped
        indent: file indentation(default-4)
    """
    try:
        with open(file, "w") as fp:
            dump(data, fp, indent=indent)
        return (None, None)
    except Exception as err:
        return (err, format_exc())