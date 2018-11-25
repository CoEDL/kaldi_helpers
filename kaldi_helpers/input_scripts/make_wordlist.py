#!/usr/bin/python3

"""
Given a json file with transcript information this tools can perform
manipulations including generating word lists.
Optionally provide the output_scripts json file name with -o

Usage: python3 make_wordlist.py [-h] -i INFILE [-o OUTFILE]
"""

import argparse
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

    arguments = parser.parse_args()
    data = load_json_file(arguments.infile)

    print("Wordlist...", flush=True, file=sys.stderr)

    word_list = extract_word_list(data)
    print("Done.", file=sys.stderr)

    print(f"Writing out wordlist to stderr...", flush=True, file=sys.stderr)
    save_word_list(word_list, arguments.outfile)
    print("Done.", file=sys.stderr)


if __name__ == '__main__':
    main()
