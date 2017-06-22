""" Converts all wav's in target dir to specified sample rate.
    WARNING: Overrites original files.

    Usage: python3 resample_wav.py <dir> <target samp rate>
"""
import sys
import os
import subprocess

import scipy.io.wavfile as wav

# Change to sox path
SOX_PATH = "/home/oadams/tools/sox-14.4.2/src/sox"

def convert_samp_rate(wav_path, tgt_rate):
    """ If the wav file is not of the given samp rate,
    convert it so that it is so.
    """

    rate, _ = wav.read(wav_path)
    if str(rate) != tgt_rate:
        print("Resampling %s from %s to %s" % (wav_path, rate, tgt_rate))
        args = [SOX_PATH, wav_path, "-r", tgt_rate, wav_path]
        subprocess.call(args)

path = sys.argv[1]
tgt_rate = sys.argv[2]

for root, dirname, filenames in os.walk(path):
    for fn in filenames:
        if fn.endswith(".wav"):
            wav_path = os.path.join(root, fn)
            convert_samp_rate(wav_path, tgt_rate)
