#!/usr/bin/python3

# Given a json file with transcript information this tools can perform
# manipulations including generating word lists.
# Optionally provide the output json file name with -j
# Usage: python filter_text.py sample.json wordlist.txt

import re
import string
import sys
import nltk
from typing import Dict, List, Set, Union
from argparse import ArgumentParser
from .utilities import load_json_file, write_dict_to_json_file


def save_word_list(word_list: List[str], file_name: str) -> None:
    """ 
    Given a list of strings, write them to a new file named filename. 
    :param word_list: list of words to write.
    :param file_name: name of file to write word list to.
    """
    with open(file_name, "w") as f:
        for word in word_list:
            f.write(word + '\n')
        print(f"Wrote word list to {file_name}")


def extract_word_list(json_data: List[Dict[str, str]]) -> List[str]:
    """
    Unpack a dictionary constructed from a json_file containing the key
    "transcript" into a (Python) list of words.
    :param json_data: python dictionary read from a JSON file.
    :return: list of unique words from data, sorted alphabetically.
    """
    result: List[str] = []
    for utterance in json_data:
        words = utterance.get("transcript").split()
        result.extend(words)
    result = list(set(result))
    return sorted(result)


def get_english_words() -> Set[str]:
    """
    Gets a list of English words from the nltk corpora (~235k words).
    N.B: will download the word list if not already available (~740kB).
    :return: a set containing the English words
    """
    nltk.download('words')
    from nltk.corpus import words
    return set(words.words())


def clean_utterance(utterance: str,
                    remove_english: bool=False,
                    english_words: set={},
                    punctuation: str=string.punctuation + "…’“–”‘°",
                    special_cases: List[str]=['<silence>']) -> (int, List[str]):
    translation_tags = {'@eng@', '<ind:', '<eng:'}
    utterance = utterance.lower()
    words = utterance.split()
    clean_words = []
    english_word_count = 0
    for word in words:
        if word in special_cases:
            continue
        if word in translation_tags:  # Translations / ignore
            return [], 0
        # If a word contains a digit, throw out whole utterance
        if bool(re.search(r'\d', word)) and not word.isdigit():
            return None
        for mark in punctuation:
            word = word.replace(mark, '')
        if remove_english and len(word) > 3 and word in english_words:
            # print(word, file=sys.stderr)
            english_word_count += 1
        clean_words.append(word)
    return english_word_count, clean_words


def filter_data(json_data: Dict[str, List[str]], remove_english=False) -> List[str]:

    # Given a data object remove any transcriptions with undesirable features
    to_remove = string.punctuation + "…’“–”‘°"
    # Any words you want to ignore
    special_cases = ["<silence>"]
    translation_tags = {'@eng@', '<ind:', '<eng:'}
    cleaned_data = []

    if remove_english:
        english_words = get_english_words()

    for utterance in json_data:
        # print(utt, file=sys.stderr)

        trans = utterance.get('transcript').lower()
        words = trans.split()

        clean_words = []
        valid_utterance = True
        eng_count = 0
        for word in words:
            # If a special case ignore
            if word in special_cases:
                continue

            # If utterance contains a translation
            if word in translation_tags:  # Translations / ignore
                break

            # If partial digit, throw out whole utterance
            if bool(re.search(r'\d', word)) and not word.isdigit():
                valid_utterance = False
                break

            # Remove punctuation and bad chars
            for char in to_remove:
                word = word.replace(char, '')

            # If word is in english dictionary count it
            if remove_english and len(word) > 3 and word in english_words:
                # print(word, file=sys.stderr)
                eng_count += 1

            clean_words.append(word)

        # Exclude utterance if empty after cleaning
        cleaned_trans = ' '.join(clean_words).strip()
        if cleaned_trans == "":
            valid_utterance = False

        # Exclude utterance if > 10% english
        if remove_english and len(clean_words) > 0 and eng_count / len(clean_words) > 0.1:
            # print(round(eng_count / len(clean_words)), trans, file=sys.stderr)
            valid_utterance = False

        # Exclude utterance if langid thinks its english
        if remove_english and use_langid and valid_utterance:
            lang, prob = identifier.classify(cleaned_trans)
            if lang == 'en' and prob > 0.5:
                valid_utterance = False

        # Something was bad in utterance
        if not valid_utterance:
            continue

        # Should be a clean valid utterance
        utterance['transcript'] = cleaned_trans
        cleaned_data.append(utterance)
    return cleaned_data


def clean_json() -> None:
    """
    Run the entire clean_json process as a command line utility.
    Usage: python clean_json.py --infile file.json [-re|--removeEng]
    """
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--infile", type=str, help="The input file to clean.")
    parser.add_argument("-re", "--removeEng", help="Remove english like utterances", action="store_true")
    args = parser.parse_args()

    data = load_json_file(args.infile)

    print("Filtering...", end='', flush=True, file=sys.stderr)

    filtered_data = filter_data(data, args.removeEng)  # mutates the data object

    write_dict_to_json_file(filtered_data, )
    # print(f_data, file=sys.stderr)
    # print("Done.", file=sys.stderr)


if __name__ == '__main__':
    clean_json()
