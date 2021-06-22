#!/usr/bin/env python3
# Import pips
import json


def load(path: str):
    '''Load configuration from file

    Args:
        path (str): the absolute path of the file to load as configuration

    Returns:
        dict: a nested dict based on the json data from the file
    '''
    with open(path, mode='r', encoding='utf-8', newline="\n") as f:
        config = json.load(f)
        return config
