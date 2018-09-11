import os
import sys
import pytest
import glob
import regex
from typing import List, Set, Dict
from scripts.trs_to_json import *

TEST_FILES_BASE_DIR = os.path.join(".", "src", "test", "testfiles")
TRS_FILE_DIR = os.path.join("C:\\", "Classified_Lang_Data", "abui-trs")
SCRIPT_PATH = os.path.join(".", "src", "scripts", "trs_to_json.py")


class TestTRSToJSON:
    def test_find_first_file_by_extension(self) -> None:
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

    def test_find_files_by_extension(self) -> None:
        all_files_in_dir = set(glob.glob(os.path.join(TEST_FILES_BASE_DIR, "**"), recursive=True))

        g_base_directory: str = TEST_FILES_BASE_DIR
        all_files_in_directory = set(glob.glob(os.path.join(g_base_directory, "**"), recursive=True))

        first_test: List[str] = find_files_by_extension(all_files_in_directory, set(["*.xlsx"]))
        files = set([os.path.split(i)[1] for i in first_test])
        assert len(first_test) == 3
        for file in first_test:
            assert file.endswith(".xlsx")
        assert {"python.xlsx", "test.xlsx", "charm.xlsx"}.issubset(files)

        second_test: List[str] = find_files_by_extension(all_files_in_directory, set(["*.py"]))
        files = set([os.path.split(i)[1] for i in second_test])
        assert len(second_test) == 1
        for file in second_test:
            assert file.endswith(".py")
        assert {"test.py"}.issubset(files)

        third_test: List[str] = find_files_by_extension(all_files_in_directory, set(["*.py", "*.txt"]))
        files = set([os.path.split(i)[1] for i in third_test])
        assert len(third_test) == 3
        for file in third_test:
            assert (file.endswith(".py") or file.endswith(".txt"))
        assert {"test.py", "howdy.txt", "test.txt"}.issubset(files)

    def test_conditional_log(self) -> None:

        sys.stderr = open('err.txt', 'w') # import not working?? check
        test_str1: str = "test"
        conditional_log(cond=True, text=test_str1);
        with open("err.txt", "r") as f:
            assert test_str1 == f.read()
            f.close()

        sys.stderr = open('err.txt', 'w')
        test_str2: str = "Kaldi is a fun project\nASR is a cool tech\n"
        conditional_log(cond=True, text=test_str2);
        with open("err.txt", "r") as f:
            assert test_str2 == f.read()
            f.close()

        sys.stderr = sys.__stderr__
        os.remove('err.txt')

    def test_process_trs_file(self):
        all_files_in_directory: Set[str] = set(glob.glob(os.path.join(TRS_FILE_DIR, "*.trs"),
                                               recursive=True))

        for file_name in all_files_in_directory:
            with open(file_name) as f:
                contents = f.read()
                count = sum(1 for match in regex.finditer(r"\bSync\b", contents, flags=regex.IGNORECASE))
                utterances = process_trs_file(file_name, False)
                assert count == len(utterances)

    def test_process_turn(self):
        all_files_in_directory: Set[str] = set(glob.glob(os.path.join(TRS_FILE_DIR, "*.trs"),
                                                         recursive=True))

        for file_name in all_files_in_directory:
            with open(file_name) as f:
                contents = f.read()
                contents_list = contents.split('\n')
                matched_lines: int = [contents_list.index(line) for line in contents_list if
                                 ("Turn" in line) and (line != '</Turn>')] + [len(contents_list)]
                tree = ET.parse(file_name)  # loads an external XML section into this element tree
                root = tree.getroot()  # root of element tree
                wave_name = root.attrib['audio_filename'] + ".wav"  # changed audio_file_name to audio_filename
                turn_nodes = tree.findall(".//Turn")

                for i in range(len(turn_nodes)):
                    turn_contents = "\n".join(contents_list[matched_lines[i]:matched_lines[i+1]])
                    count = sum(1 for match in regex.finditer(r"\bSync\b", turn_contents, flags=regex.IGNORECASE))
                    utterances_in_turn = process_turn(file_name, turn_nodes[i], wave_name, tree)
                    assert count == len(utterances_in_turn)


    def test_trs_to_JSON(self):

        num_utterances: int = 0;
        all_files_in_directory: Set[str] = set(glob.glob(os.path.join(TRS_FILE_DIR, "*.trs"),
                                                         recursive=True))
        for file_name in all_files_in_directory:
            num_utterances += len(process_trs_file(file_name, False))

        os.system("python " + SCRIPT_PATH + " --indir " + TRS_FILE_DIR)
        json_name: str = os.path.basename(TRS_FILE_DIR) + ".json"

        with open(json_name) as f:
            contents = f.read()
            count = sum(1 for match in regex.finditer(r"\bspeaker_ID\b", contents, flags=regex.IGNORECASE))

        assert count == num_utterances

        os.remove(json_name)

