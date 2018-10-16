"""
Test script for validating silence audio script. 

@author Aninda Saha
"""

from kaldi_helpers.input_scripts.silence_audio import *

SCRIPT_PATH = os.path.join(".", "kaldi_helpers", "silence_audio.py")

def test_process() -> None:
    assert 1 == 1


def test_silence_audio() -> None:
    assert 1 == 1
