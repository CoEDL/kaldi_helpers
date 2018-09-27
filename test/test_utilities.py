import sys
from src.utilities import *
from _pytest.capture import CaptureFixture

TEST_FILES_BASE_DIR = os.path.join(".", "test", "testfiles")
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
    assert out == json.dumps(EXAMPLE_JSON_DATA, indent=4) + "\n"


def test_find_first_file_by_extension() -> None:
    all_files_in_dir = list(glob.glob(os.path.join(TEST_FILES_BASE_DIR, "**"), recursive=True))
    all_files_in_dir.sort()

    first_test: str = find_first_file_by_extension(all_files_in_dir, list(["*.rtf"]))
    assert os.path.split(first_test)[1].endswith(".rtf")
    assert os.path.basename(first_test) == "test.rtf"

    second_test: str = find_first_file_by_extension(all_files_in_dir, list(["*.txt"]))
    assert os.path.split(second_test)[1].endswith(".txt")
    assert os.path.basename(second_test) != "test.txt"
    assert os.path.basename(second_test) == "howdy.txt"

    third_test: str = find_first_file_by_extension(all_files_in_dir, list(["*.py", "*.xlsx"]))
    assert os.path.split(third_test)[1].endswith(".xlsx")
    assert os.path.basename(third_test) != "howdy.xlsx"
    assert os.path.basename(third_test) == "charm.xlsx"