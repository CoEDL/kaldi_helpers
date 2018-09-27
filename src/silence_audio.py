#!/usr/bin/python3
#
# Anonymise a wave file based on an Elan tier
# Copyright Steven Bird stevenbird1@gmail.com 7 May 2016
# Adapted for mono/stero and src pipeline by Ben Foley Jan 2018
# Assumes eaf file has millisecond offsets
# Assumes do-not-publish annotations are non-overlapping
# Should work whether the Silence tier is a child tier or not

import argparse
import glob
import os
import wave
import numpy
from pympi.Elan import Eaf

def process(eaffile, DO_NOT_PUBLISH, SILENCE_M, output):
    # load audio
    with wave.open(input, 'rb') as audio:
        params = audio.getparams()
        num_channels = params.nchannels

        if params.sampwidth == 1:
            raise ValueError("Assumes 16 bit input")

        # stereo
        if (num_channels == 1) or (num_channels == 2):
            raw = audio.readframes(params.nframes * num_channels)
            samples = numpy.fromstring(raw, dtype=numpy.int16)
            samples.shape = params.nframes if num_channels == 1 else (params.nframes, 2)
        else:
            raise ValueError("Assumes mono or stereo input")

    # silence between annotations
    num_samples = 0
    scale = params.framerate / 1000

    # check tier type - is it ref or non-ref?
    silence_tier_info = eaffile.get_parameters_for_tier(DO_NOT_PUBLISH)
    silence_tier_is_a_ref_tier = True if silence_tier_info.get("PARENT_REF") else False

    print(silence_tier_is_a_ref_tier)

    if silence_tier_is_a_ref_tier:
        annotations = sorted(eaffile.get_ref_annotation_data_for_tier(DO_NOT_PUBLISH))
        print("ref_annotations")
        print(annotations)
        offsets = [int(offset * scale)
                   for (start, end, _, _) in annotations
                   for offset in (start, end)]
    else:
        annotations = sorted(eaffile.get_annotation_data_for_tier(DO_NOT_PUBLISH))
        print("annotations")
        print(annotations)
        offsets = [int(offset * scale)
                   for (start, end, _) in annotations
                   for offset in (start, end)]

    pass_thru = True
    for i in range(params.nframes):
        if offsets and i > offsets[0]:
            offsets = offsets[1:]
            pass_thru = not pass_thru
        if not pass_thru:
            samples[i] = SILENCE_M if num_channels == 1 else SILENCE_S
            num_samples += 1

    # write audio
    with wave.open(output, 'wb') as audio:
        samples.shape = params.nframes if num_channels == 1 else (params.nframes * 2)
        audio.setparams(params)
        audio.writeframesraw(samples)

    print("Silenced {} intervals ({:.1f}s)".format(len(annotations),
                                                   num_samples / params.framerate))


def main():
    """
    A command line utility to silence the audio files in a given directory 
    Usage: python silence_audio.py [--corpus <DEFAULT_DATA_DIRECTORY>] [--overwrite <true/false>]
    """

    parser = argparse.ArgumentParser(
        description="This script will silence a wave file based on annotations in an Elan tier ")
    parser.add_argument('-c', '--corpus', help='Directory of audio and eaf files', type=str, required=True)
    parser.add_argument('-s', '--silence_tier', help='silence audio when annotations are found on this tier', type=str,
                        default='Silence')
    parser.add_argument('-o', '--overwrite', help='Write over existing files', type=str, default='yes')
    args = parser.parse_args()

    corpus = args.corpus
    overwrite = args.overwrite
    DO_NOT_PUBLISH = args.silence_tier
    SILENCE_M = 0
    SILENCE_S = [0, 0]
    SUFFIX = 'S'

    # look for .eaf files, recirsively from the passed corpus dir
    # for fpath in glob.iglob(corpus + '/**/*.eaf', recursive=True):
    for fpath in glob.iglob(corpus + '/*.eaf'):
        print(fpath)
        eaffile = Eaf(fpath)
        names = eaffile.get_tier_names()
        # print(names)

        # check for existence of silence tier
        #
        if DO_NOT_PUBLISH in names:
            print("have tier %s in %s" % (DO_NOT_PUBLISH, fpath))

            basename, extn = os.path.splitext(fpath)

            input = basename + ".wav"
            if overwrite == 'yes':
                output = basename + ".wav"
            else:
                output = basename + SUFFIX + ".wav"

            process(eaffile, DO_NOT_PUBLISH, SILENCE_M, output)
            # else:
            # print("tier %s in %s not found, skipping" % (DO_NOT_PUBLISH, fpath))


if __name__ == "__main__":
    main()
