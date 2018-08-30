import os
import pytest
from typing import List
from scripts.clean_json import *


class TestSaveWordlist:
    def test_save_wordlist(self):
        file_name: str = "test.txt"
        word_list: List[str] = [
            "hello",
            "world",
            "i",
            "love",
            "tests"
        ]
        save_word_list(word_list, file_name)
        with open(file_name, "r") as file:
            assert file.read() == "\n".join(word_list)+"\n"
        os.remove("test.txt")
