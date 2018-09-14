import os
from scripts.make_wordlist import *
from typing import List


def test_save_word_list() -> None:
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
        assert file.read() == "\n".join(word_list) + "\n"
    os.remove("test.txt")  # Clean up


def test_extract_word_list() -> None:
    json_data = [
        {"transcript": "Hello world I love tests"},
        {"transcript": "I love tests too"}
    ]
    result = extract_word_list(json_data)
    assert result == ["Hello", "I", "love", "tests", "too", "world"]


