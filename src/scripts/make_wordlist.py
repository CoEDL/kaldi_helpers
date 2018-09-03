#!/usr/bin/python3
#
# Given a json file with transcript information this tools can perform
# manipulations including generating word lists.
# Optionally provide the output json file name with -j
# Usage: python filter_text.py sample.json wordlist.txt

from typing import List, Union
import argparse
import json
import sys
from .utilities import load_json_file


def save_wordlist(wordlist: List[str]) -> None:
    """
    Given a list of strings, write to a file.
    :param wordlist: list of words to write.
    """
    global args
    try:
        for word in wordlist:
            print(word + '\n', file=sys.stdout)
    except Exception as e:
        print("Could not write out to file " + args.infile, file=sys.stderr)
        exit()


def extract_word_list(data: dict) -> List[str]:
    """
    Given the data object, produce a list of string of single words.
    :param data: a dictionary with contents of the JSON file
    :return: sorted list of unique words
    """
    result = []
    for utt in data:
        words = utt.get('transcript').split()
        result.extend(words)
    result = list(set(result))
    result.sort()
    return result


def main():

    """
    Run the entire make_wordlist.py as a command line utility
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", type=str, help="The input file to clean.")
    args = parser.parse_args()

    data = load_json_file(args.infile)

    print("Wordlist...", end='', flush=True, file=sys.stderr)

    word_list = extract_word_list(data)
    print("Done.", file=sys.stderr)

    print("Write out wordlist...", end='', flush=True, file=sys.stderr)
    save_wordlist(word_list)
    print("Done.", file=sys.stderr)


if __name__ == '__main__':
    main()
