"""
Test script for validating textgrid to json conversion pipeline. 

@author Aninda Saha
"""

from src.textgrid_to_json import *

SCRIPT_PATH = os.path.join(".", "src", "textgrid_to_json.py")


def test_process_textgrid_file() -> None:

    speech_tier_total_length = 0
    for (root, dirs, files) in os.walk(TEST_FILES_BASE_DIR):
        for filename in files:
            if filename.endswith(".TextGrid"):
                tg = tgio.openTextgrid(os.path.join(root, filename))
                speech_tier_total_length += len(tg.tierDict['Speech'].entryList)

    intervals: List[Dict[str, Union[str, int]]] = process_textgrid_files(TEST_FILES_BASE_DIR)
    assert speech_tier_total_length == len(intervals)


def test_textgrid_to_json() -> None:

    utterances: List[Dict[str, Union[str, float]]] = process_textgrid_files(TEST_FILES_BASE_DIR)

    result: subprocess.CompletedProcess = subprocess.run(["python", SCRIPT_PATH, "--input_dir", TEST_FILES_BASE_DIR],
                                                         check=True)
    assert result.returncode == 0

    parent_directory_name, base_directory_name = os.path.split(TEST_FILES_BASE_DIR)
    json_name: str = os.path.join(parent_directory_name, base_directory_name + ".json")
    with open(json_name) as f:
        contents: List[Dict[str, Union[str, float]]] = json.loads(f.read())
    assert len(contents) == len(utterances)
    assert utterances == contents

    os.remove(json_name)
