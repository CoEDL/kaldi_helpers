"""
Test script for validating textgrid to json conversion pipeline. 

@author Aninda Saha
"""

import glob
from src.textgrid_to_json import *
from typing import Set

TEST_FILES_BASE_DIR = os.path.join(".", "test", "testfiles")
TEXTGRID_FILE_DIR = os.path.join("C:\\", "Classified_Lang_Data", "textgrid")
SCRIPT_PATH = os.path.join(".", "src", "scripts", "textgrid_to_json.py")


def test_process_textgrid_file() -> None:

    speech_tier_total_length = 0
    for (root, dirs, files) in os.walk(TEXTGRID_FILE_DIR):
        for filename in files:
            if filename.endswith(".TextGrid"):
                tg = tgio.openTextgrid(os.path.join(root, filename))
                speech_tier_total_length += len(tg.tierDict['Speech'].entryList)

    intervals: List[Dict[str, Union[str, int]]] = process_textgrid_file(TEXTGRID_FILE_DIR)
    assert speech_tier_total_length == len(intervals)


def test_textgrid_to_json() -> None:
    assert 1 == 1


