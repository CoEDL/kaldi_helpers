import os
from _pytest.capture import CaptureFixture
from src.clean_json import *
from src.utilities import write_data_to_json_file

EXAMPLE_JSON_DATA = [
    {"transcript": "Comment t'appelles tu?"},
    {"transcript": "Je m'appelle François."},
    {"transcript": "Est-ce tu a une livre préférér."},
    {"transcript": "Oui, j'adore L'histoire secrète par Donna Tartt."},
    {"transcript": "Vraiment? Je n'ai jamais lu ça."},
]


def test_get_english_words() -> None:
    english_words = get_english_words()
    assert "test" in english_words
    assert "français" not in english_words


def test_clean_utterance_remove_english() -> None:
    example_utterance = {"transcript": "je veux une petite dejeuner"}
    english_words = get_english_words()
    cleaned_utterance, english_word_count = clean_utterance(example_utterance,
                                                            remove_english=True,
                                                            english_words=english_words,
                                                            punctuation="…’“–”‘°",
                                                            special_cases=['<silence>'])
    assert cleaned_utterance == ['je', 'veux', 'une']  # Apparently dejeuner is in English?
    assert english_word_count == 2


def test_clean_utterance_keep_english() -> None:
    example_utterance = {"transcript": "I say, jeune homme!"}
    english_words = get_english_words()
    cleaned_utterance, english_word_count = clean_utterance(example_utterance,
                                                            remove_english=True,
                                                            english_words=english_words,
                                                            punctuation="…,’“–”‘°!",
                                                            special_cases=['<silence>'])
    assert cleaned_utterance == ['i', 'say', 'jeune', 'homme']
    assert english_word_count == 0


def test_is_valid_utterance_remove_english() -> None:
    cleaned_utterance = ['je', 'veux', 'acheter', 'la', 'nouveau', 'bonbon', 'pour', 'ma', 'mère',
                         'et', 'mon', 'père']
    langid_identifier = LanguageIdentifier.from_modelstring(model,
                                                            norm_probs=True)
    assert is_valid_utterance(clean_words=cleaned_utterance,
                              english_word_count=0,
                              remove_english=True,
                              use_langid=True,
                              langid_identifier=langid_identifier) is True


def test_is_valid_utterance_keep_english() -> None:
    cleaned_utterance = ['i', 'say', 'jeune', 'homme']
    langid_identifier = LanguageIdentifier.from_modelstring(model,
                                                            norm_probs=True)
    assert is_valid_utterance(clean_words=cleaned_utterance,
                              english_word_count=0,
                              remove_english=False,
                              use_langid=False,
                              langid_identifier=langid_identifier) is True


def test_clean_json_data_full() -> None:
    clean_data = clean_json_data(EXAMPLE_JSON_DATA,
                                 remove_english=True,
                                 use_langid=True)
    print(clean_data)
    assert clean_data == [
        {"transcript": "je mappelle françois"},
        {"transcript": "vraiment je nai jamais lu ça"}
    ]


def test_clean_json_data_full_file() -> None:
    file_in_name = 'file_in.json'
    file_out_name = 'file_out.json'
    # os.system('touch file_out.json') # Not Windows compatible
    open(file_out_name, 'w')
    write_data_to_json_file(EXAMPLE_JSON_DATA, file_in_name)
    os.system(f"clean_json.py --infile {file_in_name} --outfile {file_out_name}"
              f" --removeEng --useLangid")
    # assert load_json_file(file_out_name) == [
    #     {"transcript": "je mappelle françois"},
    #     {"transcript": "vraiment je nai jamais lu ça"}
    # ]
    os.remove(file_in_name)
    os.remove(file_out_name)


def test_clean_json_data_full_command_line(capsys: CaptureFixture) -> None:
    pass
