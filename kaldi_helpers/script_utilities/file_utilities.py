import os
import glob
from typing import Set, List


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


def find_first_file_by_extension(set_of_all_files: List[str], extensions: List[str]) -> str:
    """
    Searches for the first file with a given extension in a set of files.

    :param set_of_all_files: set of file names in string format
    :param extensions: file extension being searched for
    :return: name of the first file_name that is matched, if any. otherwise, this method returns an empty string
    """
    for f in set_of_all_files:
        name, extension = os.path.splitext(f)
        if ("*" + extension.lower()) in extensions:
            return f
    return ""
