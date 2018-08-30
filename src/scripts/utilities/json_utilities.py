import json


def load_json_file(file_name: str) -> dict:
    """
    Given a filename (parameter) containing JSON, load and
    return the a Python dictionary with containing the same information.
    :param file_name: name of file containing JSON to read from.
    :return a Python dictionary with the contents of the JSON file.
    """
    if file_name:
        file = open(file_name, "r", encoding="utf-8")
        data: dict = json.load(file)
        return data
