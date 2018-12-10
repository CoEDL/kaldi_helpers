#!/usr/bin/python3

"""
Given a json file with transcript information this tools can perform
manipulations including generating word lists.
Optionally provide the output_scripts json file name with -o

Usage: python3 make_wordlist.py [-h] -i INFILE [-o OUTFILE]
"""

import argparse
import glob
import os
import sys
from typing import List, Dict
from kaldi_helpers.script_utilities import load_json_file, find_files_by_extensions


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
    :param kaldi_corpus: the path to kaldi corpus.txt file created by json_to_kaldi.py.
    """
    if not os.path.exists(kaldi_corpus):
        print(f"Failed to find corpus.txt file at {kaldi_corpus}.")
    else:
        with open(kaldi_corpus, "a") as kaldi_corpus_file:
            if os.path.exists(file_name):
                print(f"Extracting corpus examples from: {file_name}")
                with open(file_name, "r", encoding="utf-8",) as file_:
                    for line in file_:
                        kaldi_corpus_file.writelines(line)
            else:
                print("Provided additional text corpus invalid")


def generate_word_list(transcription_file: str,
                       word_list_file: str,
                       text_corpus_directory: str,
                       output_file: str,
                       kaldi_corpus_file: str) -> None:
    """
    Generates the wordlist.txt file used to populate the Kaldi file structure and generate
    the lexicon.txt file.
    :param transcription_file: path to the json file containing the transcriptions
    :param word_list_file: the path of the file to write the word list to
    :param text_corpus_directory: file path to a folder of text-only corpus files to include in corpus.txt
    :param output_file: the path of the file to write the word list to
    :param kaldi_corpus_file: file path to the corpus.txt created by json_to_kaldi.py
    :return:
    """
    json_data: List[Dict[str, str]] = load_json_file(transcription_file)

    if word_list_file and os.path.exists(word_list_file):
        print(f"Using additional word list at {word_list_file}")
        additional_words = extract_additional_words(word_list_file)
    else:
        print("No additional word list provided or provided list invalid...")
        additional_words = []

    if text_corpus_directory:
        print(f"Using additional text corpus at {text_corpus_directory}")
        all_files_in_dir = set(glob.glob(os.path.join(text_corpus_directory, "**"), recursive=True))
        for corpora_file in find_files_by_extensions(all_files_in_dir, {"txt"}):
            additional_words = additional_words.extend(extract_additional_words(corpora_file))
            extract_additional_corpora(corpora_file, kaldi_corpus_file)
    else:
        print("No additional text corpus provided.")

    print("Extracting word list(s)...", flush=True, file=sys.stderr)

    # Retrieve ELAN word data
    word_list_file = extract_word_list(json_data)

    # Add additional words to lexicon if required
    word_list_file.extend(additional_words)

    # Remove duplicates
    word_list_file = list(set(word_list_file))

    print(f"Writing wordlist to file...", flush=True, file=sys.stderr)
    save_word_list(word_list_file, output_file)


def main():
    """
    Run the entire make_wordlist.py as a command line utility.
    
    Usage: python3 make_wordlist.py [-h] -i INFILE [-o OUTFILE] [-w WORDLIST] [-t TEXTCORPUS] [-c KALDICORPUS]
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
    parser.add_argument("-w", "--word_list",
                        type=str,
                        required=False,
                        help="File path to an optional additional word list.")
    parser.add_argument("-t", "--text_corpus",
                        help="File path to a folder of text-only corpus files to include in corpus.txt.",
                        required=False)
    parser.add_argument("-c", "--kaldi_corpus",
                        type=str,
                        help="File path to the corpus.txt created by json_to_kaldi.py.",
                        required=True)
    arguments = parser.parse_args()

    generate_word_list(transcription_file=arguments.infile,
                       word_list_file=arguments.word_list,
                       text_corpus_directory=arguments.text_corpus,
                       output_file=arguments.outfile,
                       kaldi_corpus_file=arguments.kaldi_corpus)

    print("Done.", file=sys.stderr)


if __name__ == '__main__':
    main()
