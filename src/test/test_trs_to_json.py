import os
import sys
import pytest
import glob
from typing import List, Set, Dict
from scripts.trs_to_json import *
# Capsys

class TestTRSToJSON:

    def test_find_first_file_by_ext(self) -> None:

        g_base_dir = ".\\src\\test\\testfiles\\"
        all_files_in_dir = list(glob.glob(os.path.join(g_base_dir, "**"), recursive=True))
        all_files_in_dir.sort()
        
        first_test: str = find_first_file_by_ext(all_files_in_dir, list(["*.rtf"]))
        assert os.path.split(first_test)[1].endswith(".rtf")
        assert os.path.basename(first_test) == "test.rtf"

        second_test: str = find_first_file_by_ext(all_files_in_dir, list(["*.txt"]))
        assert os.path.split(second_test)[1].endswith(".txt")
        assert os.path.basename(second_test) != "test.txt"
        assert os.path.basename(second_test) == "howdy.txt"

        third_test: str = find_first_file_by_ext(all_files_in_dir, list(["*.py", "*.xlsx"]))
        assert os.path.split(third_test)[1].endswith(".xlsx")
        assert os.path.basename(third_test) != "howdy.xlsx"
        assert os.path.basename(third_test) == "charm.xlsx"

    def test_find_files_by_ext(self) -> None:

        g_base_dir = ".\\src\\test\\testfiles\\"
        all_files_in_dir = set(glob.glob(os.path.join(g_base_dir, "**"), recursive=True))

        first_test: List[str] = find_files_by_ext(all_files_in_dir, set(["*.xlsx"]))
        files = set([os.path.split(i)[1] for i in first_test])
        assert len(first_test) == 3
        for file in first_test:
            assert file.endswith(".xlsx")
        assert {"python.xlsx", "test.xlsx", "charm.xlsx"}.issubset(files)

        second_test: List[str] = find_files_by_ext(all_files_in_dir, set(["*.py"]))
        files = set([os.path.split(i)[1] for i in second_test])
        assert len(second_test) == 1
        for file in second_test:
            assert file.endswith(".py")
        assert {"test.py"}.issubset(files)

        third_test: List[str] = find_files_by_ext(all_files_in_dir, set(["*.py", "*.txt"]))
        files = set([os.path.split(i)[1] for i in third_test])
        assert len(third_test) == 3
        for file in third_test:
            assert (file.endswith(".py") or file.endswith(".txt"))
        assert {"test.py", "howdy.txt", "test.txt"}.issubset(files)


    def test_cond_log(self):

        sys.stderr = open('err.txt', 'w') # import not working?? check
        test_str1: str = "test"
        cond_log(cond=True, text=test_str1);
        with open("err.txt", "r") as f:
            assert test_str1 == f.read()
            f.close()

        sys.stderr = open('err.txt', 'w')
        test_str2: str = "Kaldi is a fun project\nASR is a cool tech\n"
        cond_log(cond=True, text=test_str2);
        with open("err.txt", "r") as f:
            assert test_str2 == f.read()
            f.close()

        sys.stderr = sys.__stderr__
        os.remove('err.txt')

    def test_process_file(self):
        assert 1 == 1

    def test_process_turn(self):
        assert 1 == 1

    def test_trs_to_JSON(self):
        assert 1 == 1