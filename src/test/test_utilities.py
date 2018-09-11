import os
import sys
from _pytest.capture import CaptureFixture
from utilities.json_utilities import *


TEST_FILES_BASE_DIR = os.path.join(".", "src", "test", "testfiles")
EXAMPLE_JSON_DATA = [
    {"transcript": "Comment t'appelles tu?"},
    {"transcript": "Je m'appelle François."},
    {"transcript": "Est-ce tu a une livre préférér."},
    {"transcript": "Oui, j'adore L'histoire secrète par Donna Tartt."},
    {"transcript": "Vraiment? Je n'ai jamais lu ça."},
]


def test_load_json_file():
    json_data = load_json_file(os.path.join(TEST_FILES_BASE_DIR, "example.json"))
    assert json_data[0]["transcript"] == "¿Por qué no los dos?"


def test_write_data_to_json_file_path():
    write_data_to_json_file(EXAMPLE_JSON_DATA, "test_file.json")
    with open("test_file.json", "r") as test_file:
        assert json.load(test_file) == EXAMPLE_JSON_DATA
    os.remove('test_file.json')


def test_write_data_to_json_stdout(capsys: CaptureFixture):
    write_data_to_json_file(EXAMPLE_JSON_DATA, sys.stdout)
    out, _ = capsys.readouterr()
    assert out == json.dumps(EXAMPLE_JSON_DATA, indent=2) + "\n"
