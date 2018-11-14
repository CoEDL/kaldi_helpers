import os

# Used by test scripts to tap into a folder of testfiles
TEST_FILES_BASE_DIR = os.path.join(".", "test", "testfiles")
DEFAULT_DATA_DIRECTORY = os.path.join(".", "resources", "corpora", "abui_toy_corpus", "data")

# Used by resample_to_audio
AUDIO_EXTENSIONS = ["*.wav"]
TEMPORARY_DIRECTORY = "tmp"
SOX_PATH = os.path.join("C:\\", "Program Files (x86)", "sox-14-4-2", "sox.exe")
#SOX_PATH = os.path.join("..", "usr", "bin", "sox")

# Used by json_to_kaldi
# WAV_FOLDER: str = "wavs/"
