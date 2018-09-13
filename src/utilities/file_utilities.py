import os
from typing import Set


def find_files_by_extension(set_of_all_files: Set[str], extensions: Set[str]) -> Set[str]:
    """
    Searches for all files in the set of files with the given extensions.
    :param set_of_all_files: set of file names in string format
    :param extensions: file extension being searched for
    :return: list of file_names matched with given extension. if none exists, returns an empty list.
    """
    results = set()

    for f in set_of_all_files:
        name, extension = os.path.splitext(f)
        if ("*" + extension.lower()) in extensions:
            results.add(f)
    return results
