""" Converts all wav's in target dir to standard RIFF, mono, with specified sample rate.
    WARNING: Overwrites original files.

    Usage: python3 resample_wav.py <dir> <target samp rate>
"""
import sys
import os
from subprocess import call

import scipy.io.wavfile as wav

# Change to sox path
SOX_PATH = "/home/oadams/tools/sox-14.4.2/src/sox"

def process(filename):

    name = filename.rsplit(".", 1)[0];

    input_name = name + ".wav";
    riff_name = name + "_riff.wav";
    mono_name = name + "_mono.wav";

    print(input_name)

    call(SOX_PATH + " '" + input_name + "' '" + riff_name + "'", shell=True);
    call(SOX_PATH + " '" + riff_name + "' '" + mono_name + "' remix 1", shell=True);
    call("mv '" + mono_name + "' '" + input_name + "'", shell=True);

    call("rm '" + "' '".join([riff_name]) + "'", shell=True);

def convert_samp_rate(wav_path, tgt_rate):
    """ If the wav file is not of the given samp rate,
    convert it so that it is so.
    """

    rate, _ = wav.read(wav_path)
    if str(rate) != tgt_rate:
        print("Resampling %s from %s to %s" % (wav_path, rate, tgt_rate))
        prefix, ext = os.path.splitext(wav_path)
        resample_path = prefix + "resample.wav"
        args = [SOX_PATH, wav_path, "-r", tgt_rate, resample_path]
        call(args)
        call(["mv", resample_path, wav_path])

path = sys.argv[1]
tgt_rate = sys.argv[2]

for root, dirname, filenames in os.walk(path):
    for fn in filenames:
        if fn.endswith(".wav"):
            wav_path = os.path.join(root, fn)
            process(wav_path)
            convert_samp_rate(wav_path, tgt_rate)
