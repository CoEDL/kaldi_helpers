"""
Test script for validating resample audio script. 

@author Aninda Saha
"""

from src.resample_audio import *

SCRIPT_PATH = os.path.join(".", "src", "resample_audio.py")


def test_join_normalised_path() -> None:

    path1: str = os.path.join(".", "cupboard", "narnia")
    path2: str = os.path.join("..", "castle")

    normalised_path: str = join_normalised_path(path1, path2)
    assert normalised_path == os.path.join("cupboard", "castle")


def test_resample_audio() -> None:

    result: subprocess.CompletedProcess = subprocess.run(["python", SCRIPT_PATH, "--corpus", DEFAULT_DATA_DIRECTORY],
                                                         check=True)
    assert result.returncode == 0

    all_files_in_directory: Set[str] = set(glob.glob(os.path.join(DEFAULT_DATA_DIRECTORY, "*.wav"),
                                                     recursive=True))
    print("all files:", all_files_in_directory)

    for file in all_files_in_directory:
        process: subprocess.Popen = subprocess.Popen([SOX_PATH, "--i", "-r", os.path.join(DEFAULT_DATA_DIRECTORY, os.path.basename(file))],
                                stdout=subprocess.PIPE)
        sample_rate: str = process.stdout.read()
        assert int(sample_rate) == 44100


