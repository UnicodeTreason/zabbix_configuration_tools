#!/usr/bin/env python3
# Import pips
import os
import re
import json


def load(dir: str, pattern: str) -> dict:
    '''Load validation from files in specified dir

    Args:
        dir (str):     the absolute path of the dir to load validation from
        pattern (str): the REGEX pattern to ensure only desired files are loaded

    Returns:
        dict: a nested dict based on the json data from the files
    '''
    validation = {}

    with os.scandir(dir) as files:
        for entry in files:
            if entry.is_file():
                if re.match(pattern, entry.name):
                    with open(entry.path, mode='r', encoding='utf-8', newline="\n") as f:
                        validation[f'{entry.name}'] = json.load(f)

    return validation
