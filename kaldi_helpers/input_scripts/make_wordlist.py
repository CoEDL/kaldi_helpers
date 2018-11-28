#!/usr/bin/python3

"""
Given a json file with transcript information this tools can perform
manipulations including generating word lists.
Optionally provide the output_scripts json file name with -o

Usage: python3 make_wordlist.py [-h] -i INFILE [-o OUTFILE]
"""

import argparse
import os
import sys
from typing import List, Dict
from kaldi_helpers.script_utilities import load_json_file


def save_word_list(word_list: List[str], file_name: str) -> None:
    """
    Given a list of strings, write them to a new file named filename.
    :param word_list: list of words to write.
    :param file_name: name of file to write word list to.
    """
    with open(file_name, "w", encoding='utf-8') as f:
        for word in word_list:
            f.write(word + "\n",)
        print(f"Wrote word list to {file_name}")


def extract_word_list(json_data: List[Dict[str, str]]) -> List[str]:
    """
    Unpack a dictionary constructed from a json_file - containing the key
    "transcript" - into a (Python) list of words.
    :param json_data: Python list of dictionaries read from a JSON file.
    :return: list of unique words from data, sorted alphabetically.
    """
    result: List[str] = []
    for utterance in json_data:
        words = utterance.get("transcript").split()
        result.extend(words)
    result = list(set(result))
    return sorted(result)


def extract_additional_words(file_name) -> List[str]:
    """
    Extracts additional words from an additional text file for the purpose
    of extending the lexicon to words that there is no sound data for.
    :param file_name: the name of the file to extract words from.
    :return: a list of words
    """
    words = []
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            for line in f.readlines():
                new_words = line.split(" ")
                words.extend(new_words)
    else:
        print("WARNING: Additional word list file does not exist, skipping!")
    return words


def main():
    """
    Run the entire make_wordlist.py as a command line utility.
    
    Usage: python3 make_wordlist.py [-h] -i INFILE [-o OUTFILE]
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile",
                        type=str,
                        required=True,
                        help="The json file containing the transcript.")
    parser.add_argument("-o", "--outfile",
                        type=str,
                        required=True,
                        help="The path of the file to write the wordlist to.")
    parser.add_argument("-w", "--wordlist",
                        type=str,
                        required=False,
                        help="An optional additional word list file (path)")

    arguments = parser.parse_args()
    json_data: List[Dict[str, str]] = load_json_file(arguments.infile)

    if arguments.wordlist:
        additional_words = extract_additional_words(arguments.wordlist)
    else:
        additional_words = []

    print("Extracting word list(s)...", flush=True, file=sys.stderr)

    # Retrieve ELAN word data
    word_list = extract_word_list(json_data)

    # Add additional words to lexicon if required
    word_list.extend(additional_words)

    # Remove duplicates
    word_list = list(set(word_list))

    print(f"Writing wordlist to file...", flush=True, file=sys.stderr)
    save_word_list(word_list, arguments.outfile)

    print("Done.", file=sys.stderr)


if __name__ == '__main__':
    main()
