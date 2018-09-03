import os
import pytest
from typing import Set
from scripts.clean_json import *


class TestCleanJSON:
    def test_save_word_list(self) -> None:
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

    def test_extract_word_list(self) -> None:
        json_data = [
            {"transcript": "Hello world I love tests"},
            {"transcript": "I love tests too"}
        ]
        result = extract_word_list(json_data)
        assert result == ["Hello", "I", "love", "tests", "too", "world"]

    def test_get_english_words(self) -> None:
        english_words = get_english_words()
        assert "test" in english_words
        assert "français" not in english_words

    def test_clean_utterance_remove_english(self) -> None:
        example_utterance = {"transcript": "je veux une petite dejeuner"}
        english_words = get_english_words()
        cleaned_utterance, english_word_count = clean_utterance(example_utterance,
                                                                remove_english=True,
                                                                english_words=english_words,
                                                                punctuation="…’“–”‘°",
                                                                special_cases=['<silence>'])
        assert cleaned_utterance == ['je', 'veux', 'une']  # Apparently dejeuner is in English?
        assert english_word_count == 2

    def test_clean_utterance_keep_english(self) -> None:
        example_utterance = {"transcript": "I say, jeune homme!"}
        english_words = get_english_words()
        cleaned_utterance, english_word_count = clean_utterance(example_utterance,
                                                                remove_english=True,
                                                                english_words=english_words,
                                                                punctuation="…,’“–”‘°!",
                                                                special_cases=['<silence>'])
        assert cleaned_utterance == ['i', 'say', 'jeune', 'homme']  # Apparently dejeuner is in English?
        assert english_word_count == 0

    def test_is_valid_utterance_remove_english(self) -> None:
        cleaned_utterance = ['je', 'veux', 'acheter', 'la', 'nouveau', 'bonbon', 'pour', 'ma', 'mère',
                             'et', 'mon', 'père']
        langid_identifier = LanguageIdentifier.from_modelstring(model,
                                                                norm_probs=True)
        assert is_valid_utterance(clean_words=cleaned_utterance,
                                  english_word_count=0,
                                  remove_english=True,
                                  use_langid=True,
                                  langid_identifier=langid_identifier) is True

    def test_is_valid_utterance_keep_english(self) -> None:
        cleaned_utterance = ['i', 'say', 'jeune', 'homme']
        langid_identifier = LanguageIdentifier.from_modelstring(model,
                                                                norm_probs=True)
        assert is_valid_utterance(clean_words=cleaned_utterance,
                                  english_word_count=0,
                                  remove_english=False,
                                  use_langid=False,
                                  langid_identifier=langid_identifier) is True
