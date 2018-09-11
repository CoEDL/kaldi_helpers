import os
import sys
import pytest
import glob
import regex
from typing import List, Set, Dict
from scripts.textgrid_to_json import *

TEST_FILES_BASE_DIR = os.path.join(".", "src", "test", "testfiles")
TEXTGRID_FILE_DIR = os.path.join("C:\\", "Classified_Lang_Data", "textgrid")
SCRIPT_PATH = os.path.join(".", "src", "scripts", "textgrid_to_json.py")

class TestTextgridToJSON:

    def test_process_textgrid_file(self) -> None:
        all_files_in_dir: Set[str] = set(glob.glob(os.path.join(TEXTGRID_FILE_DIR, "**"), recursive=True))
        intervals: List[Dict[str, Union[str, int]]] = process_textgrid_file(TEXTGRID_FILE_DIR)

        assert 198 == len(intervals)

    def test_write_json(self) -> None:

        assert 1 == 1

    def test_textgrid_to_json(self) -> None:
        assert 1 == 1


