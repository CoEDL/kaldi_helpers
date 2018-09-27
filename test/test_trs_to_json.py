"""
Test script for validating trs to json conversion methods. 

@author Aninda Saha
"""

from src.trs_to_json import *

SCRIPT_PATH = os.path.join(".", "src", "trs_to_json.py")

def test_find_files_by_extension() -> None:

    all_files_in_directory: List[str] = set(glob.glob(os.path.join(TEST_FILES_BASE_DIR, "**"), recursive=True))

    first_test: List[str] = find_files_by_extension(all_files_in_directory, set(["*.xlsx"]))
    files = set([os.path.split(i)[1] for i in first_test])
    assert len(first_test) == 3 # Number of .xlsx files stored in testfiles folder
    for file in first_test:
        assert file.endswith(".xlsx")
    assert {"python.xlsx", "test.xlsx", "charm.xlsx"}.issubset(files)

    second_test: List[str] = find_files_by_extension(all_files_in_directory, set(["*.py"]))
    files = set([os.path.split(i)[1] for i in second_test])
    assert len(second_test) == 1 # Number of .py files stored in testfiles folder
    for file in second_test:
        assert file.endswith(".py")
    assert {"test.py"}.issubset(files)

    third_test: List[str] = find_files_by_extension(all_files_in_directory, set(["*.py", "*.txt"]))
    files = set([os.path.split(i)[1] for i in third_test])
    assert len(third_test) == 3 # Total number of .py and .txt files stored in testfiles folder
    for file in third_test:
        assert (file.endswith(".py") or file.endswith(".txt"))
    assert {"test.py", "howdy.txt", "test.txt"}.issubset(files)


def test_conditional_log() -> None:

    sys.stderr: TextIOWrapper = open('err.txt', 'w')
    test_str1: str = "test"
    conditional_log(condition=True, text=test_str1);
    with open("err.txt", "r") as f:
        assert test_str1 == f.read()
        f.close()

    sys.stderr: TextIOWrapper = open('err.txt', 'w')
    test_str2: str = "Kaldi is a fun project\nASR is a cool tech\n"
    conditional_log(condition=True, text=test_str2);
    with open("err.txt", "r") as f:
        assert test_str2 == f.read()
        f.close()

    sys.stderr = sys.__stderr__
    os.remove('err.txt')


def test_process_trs_file():
    all_files_in_directory: Set[str] = set(glob.glob(os.path.join(TEST_FILES_BASE_DIR, "*.trs"),
                                           recursive=True))
    for file_name in all_files_in_directory:
        with open(file_name) as f:
            contents: str = f.read()
            count: int = sum(1 for match in regex.finditer(r"\bSync\b", contents, flags=regex.IGNORECASE))
            utterances: List[Dict[str, Union[str, float]]] = process_trs_file(file_name, False)
            assert count == len(utterances)


def test_process_turn():
    all_files_in_directory: Set[str] = set(glob.glob(os.path.join(TEST_FILES_BASE_DIR, "*.trs"),
                                                     recursive=True))

    for file_name in all_files_in_directory:
        with open(file_name) as f:
            contents: str = f.read()
            contents_list: List[str] = contents.split('\n')
            matched_lines: int = [contents_list.index(line) for line in contents_list if
                             ("Turn" in line) and (line != '</Turn>')] + [len(contents_list)]
            tree: ET.ElementTree = ET.parse(file_name)
            root: ET.Element = tree.getroot()
            wave_name: str = root.attrib['audio_filename'] + ".wav"
            turn_nodes: List[ET.Element] = tree.findall(".//Turn")

            for i in range(len(turn_nodes)):
                turn_contents: str = "\n".join(contents_list[matched_lines[i]:matched_lines[i+1]])
                count: int = sum(1 for match in regex.finditer(r"\bSync\b", turn_contents, flags=regex.IGNORECASE))
                utterances_in_turn: List[Dict[str, Union[str, float]]] = process_turn(wave_name, turn_nodes[i], tree)
                assert count == len(utterances_in_turn)


def test_trs_to_json():
    all_files_in_directory: Set[str] = set(glob.glob(os.path.join(TEST_FILES_BASE_DIR, "*.trs"),
                                                     recursive=True))
    utterances: List[Dict[str, Union[str, float]]] = []
    for file_name in all_files_in_directory:
        utterances = utterances + process_trs_file(file_name, False)

    result: subprocess.CompletedProcess = subprocess.run(["python", SCRIPT_PATH, "--input_dir", TEST_FILES_BASE_DIR], check=True)
    assert result.returncode == 0

    parent_directory_name, base_directory_name = os.path.split(TEST_FILES_BASE_DIR)
    json_name: str = os.path.join(parent_directory_name, base_directory_name+".json")
    with open(json_name) as f:
        contents: List[Dict[str, Union[str, float]]] = json.loads(f.read())
    os.remove(json_name)

    assert (len(contents) == len(utterances))
    assert contents == utterances

