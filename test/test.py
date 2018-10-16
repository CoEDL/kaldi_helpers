import os
import glob
import subprocess
from kaldi_helpers.script_utilities import find_files_by_extension

TEST_FILES_BASE_DIR = os.path.normpath(os.path.join(os.getcwd(), os.path.join(".", "testfiles")))
SCRIPT_PATH = os.path.normpath(os.path.join(os.getcwd(), os.path.join("..", "kaldi_helpers", "trs_to_json.py")))

# all_files_in_dir = list(glob.glob(os.path.join(SCRIPT_PATH, "*.py"), recursive=True))

print(TEST_FILES_BASE_DIR)
print(SCRIPT_PATH)

subprocess.call(["python", SCRIPT_PATH, "--indir", TEST_FILES_BASE_DIR])

# print(all_files_in_dir)