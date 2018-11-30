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


def extract_additional_words(file_name: str) -> List[str]:
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


def extract_additional_corpora(file_name: str, kaldi_corpus: str) -> None:
    """
    Takes a text file, extracts all sentences and writes them to the corpus file.
    :param file_name: the path to a plaintext file to extract additional sentences/lines from
    :param kaldi_corpus: the path to kaldi corpus.txt file created by
    :return: a list of additional example sentences with no associated audio data
    """
    if not os.path.exists(kaldi_corpus):
        print(f"Failed to find corpus.txt file at {kaldi_corpus}.")
    else:
        with open(kaldi_corpus, "a") as kaldi_corpus_file_:
            if os.path.exists(file_name):
                with open(file_name, "r", encoding="utf-8",) as file_:
                    for line in file_:
                        kaldi_corpus_file_.writelines(line)
            else:
                print("Provided additional text corpus invalid")



def main():
    """
    Run the entire make_wordlist.py as a command line utility.
    
    Usage: python3 make_wordlist.py [-h] -i INFILE [-o OUTFILE] [-w WORDLIST] [-t TEXTCORPUS]
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile",
                        type=str,
                        required=True,
                        help="The json file containing the transcriptions.")
    parser.add_argument("-o", "--outfile",
                        type=str,
                        required=True,
                        help="The path of the file to write the word list to.")
    parser.add_argument("-w", "--wordlist",
                        type=str,
                        required=False,
                        help="File path to an optional additional word list")
    parser.add_argument("-t", "--text_corpus",
                        help="File path to an additional text-only corpus file to include in corpus.txt",
                        required=False)
    parser.add_argument("-c", "--kaldi_corpus",
                        type=str,
                        help="File path to the corpus.txt created by json_to_kaldi.py",
                        required=True)
    arguments = parser.parse_args()
    json_data: List[Dict[str, str]] = load_json_file(arguments.infile)

    if arguments.wordlist and os.path.exists(arguments.wordlist):
        print(f"Using additional word list at {arguments.wordlist}")
        additional_words = extract_additional_words(arguments.wordlist)
    else:
        print("No additional word list provided or provided list invalid...")
        additional_words = []

    if arguments.text_corpus:
        print(f"Using additional text corpus at {arguments.text_corpus}")
        additional_words = additional_words.extend(extract_additional_words(arguments.text_corpus))
        extract_additional_corpora(arguments.text_corpus, arguments.kaldi_corpus)
    else:
        print("No additional text corpus provided.")

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
