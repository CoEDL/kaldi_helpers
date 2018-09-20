"""
Test script for validating textgrid to json conversion pipeline. 

@author Aninda Saha
"""


from src.textgrid_to_json import *

TEST_FILES_BASE_DIR = os.path.join(".", "test", "testfiles")
SCRIPT_PATH = os.path.join(".", "src", "scripts", "textgrid_to_json.py")

def test_process_textgrid_file() -> None:

    speech_tier_total_length = 0
    for (root, dirs, files) in os.walk(TEST_FILES_BASE_DIR):
        for filename in files:
            if filename.endswith(".TextGrid"):
                tg = tgio.openTextgrid(os.path.join(root, filename))
                speech_tier_total_length += len(tg.tierDict['Speech'].entryList)

    intervals: List[Dict[str, Union[str, int]]] = process_textgrid_file(TEST_FILES_BASE_DIR)
    assert speech_tier_total_length == len(intervals)


def test_textgrid_to_json() -> None:

    num_utterances: int = 0;
    all_files_in_directory: Set[str] = set(glob.glob(os.path.join(TEST_FILES_BASE_DIR, "*.textgrid"),
                                                     recursive=True))
    for file_name in all_files_in_directory:
        num_utterances += len(process_textgrid_file(file_name))

    os.system("python " + SCRIPT_PATH + " --indir " + TEST_FILES_BASE_DIR)

    json_name: str = os.path.basename(TEST_FILES_BASE_DIR) + ".json"
    with open(json_name) as f:
        contents = f.read()
        count = sum(1 for match in regex.finditer(r"\bspeaker_ID\b", contents, flags=regex.IGNORECASE))

    assert count == num_utterances

    os.remove(json_name)