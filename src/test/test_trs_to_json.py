import os
import pytest
import glob
from typing import List, Set
from scripts.trs_to_json import *


class TestTrsToJson:

    def test_find_first_file_by_ext(self):
        g_base_dir = ".\\src\\test\\testfiles\\"
        all_files_in_dir = set(glob.glob(os.path.join(g_base_dir, "**"), recursive=True))

        first_file: str = find_first_file_by_ext(all_files_in_dir, ".rtf")

        assert first_file == "test.rtf"


