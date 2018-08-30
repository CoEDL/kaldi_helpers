import os
import pytest
from typing import List
from scripts.clean_json import *


class TestSaveWordlist:
    def test_save_wordlist(self):
        filename: str = 'test.txt'
        wordlist: List[str] = [
            'hello',
            'world',
            'i',
            'love',
            'tests'
        ]
        save_word_list(wordlist, filename)
        with open(filename, 'r') as file:
            assert file.read() == '\n'.join(wordlist)+'\n'
        os.remove("test.txt")
