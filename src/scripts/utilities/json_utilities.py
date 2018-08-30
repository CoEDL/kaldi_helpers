"""
Collection of utilities for working with JSON files.
"""

import json
from typing import Union
from _io import TextIOWrapper


def load_json_file(file_name: str) -> dict:
    """
    Given a filename (parameter) containing JSON, load and
    return the a Python dictionary with containing the same information.
    :param file_name: name of file containing JSON to read from.
    :return a Python dictionary with the contents of the JSON file.
    """
    file = open(file_name, "r", encoding="utf-8")
    data: dict = json.load(file)
    return data


def write_dict_to_json_file(data: dict, output: Union[str, TextIOWrapper]) -> None:
    """
    Writes the given Python dictionary object to a JSON file at the the given
    output location (which can either be a file - specified as a string, or
    directed to an output like sys.stdout or sys.stderr).
    :param data: the Python dictionary to be converted to JSON and written.
    :param output: the file to write the dictionary contents to.
    """
    if isinstance(output, str):
        output = open(output, "w")
    print(json.dumps(data, indent=2), file=output)