#!/usr/bin/python3

""" 
Anonymise a wave file based on an Elan tier
Copyright Steven Bird stevenbird1@gmail.com 7 May 2016
Adapted for mono/stero and src pipeline by Ben Foley Jan 2018
Assumes eaf file has millisecond offsets
Assumes do-not-publish annotations are non-overlapping
Should work whether the Silence tier is a child tier or not

Usage: 
"""

import argparse
import glob
import os
import wave
import numpy
import sys
from pyparsing import ParseException
from pympi.Elan import Eaf

def silence_audio(eaf_file, output, silence_mono, silence_stereo, do_not_publish):

    # Load the audio file
    with wave.open(input, "rb") as audio:
        parameters = audio.getparams()
        number_of_channels = parameters.nchannels

        if parameters.sample_width == 1:
            raise ValueError("Assumes 16 bit input")

        # Stereo audio file handling
        if (number_of_channels == 1) or (number_of_channels == 2):
            raw_audio = audio.readframes(parameters.nframes * number_of_channels)
            samples = numpy.fromstring(raw_audio, dtype=numpy.int16)
            samples.shape = parameters.nframes if number_of_channels == 1 else (parameters.nframes, 2)
        else:
            raise ValueError("Assumes mono or stereo input")

    # Silence between annotations
    number_of_samples = 0
    scale = parameters.framerate / 1000

    # Check tier type of the silence tier - is it a reference tier?
    silence_tier_info = eaf_file.get_parameters_for_tier(do_not_publish)
    is_reference_tier = bool(silence_tier_info.get("PARENT_REF"))

    if is_reference_tier:
        annotations = sorted(eaf_file.get_ref_annotation_data_for_tier(do_not_publish))
        print("ref_annotations")
        print(annotations)
        offsets = [int(offset * scale)
                   for (start, end, _, _) in annotations
                   for offset in (start, end)]
    else:
        annotations = sorted(eaf_file.get_annotation_data_for_tier(do_not_publish))
        print("annotations")
        print(annotations)
        offsets = [int(offset * scale)
                   for (start, end, _) in annotations
                   for offset in (start, end)]

    pass_through = True
    for i in range(parameters.nframes):
        if offsets and i > offsets[0]:
            offsets = offsets[1:]
            pass_through = not pass_through
        if not pass_through:
            samples[i] = silence_mono if number_of_channels == 1 else silence_stereo
            number_of_samples += 1

    # write audio
    with wave.open(output, 'wb') as audio:
        samples.shape = parameters.nframes if number_of_channels == 1 else (parameters.nframes * 2)
        audio.setparams(parameters)
        audio.writeframesraw(samples)

    print("Silenced {} intervals ({:.1f}s)".format(len(annotations),
                                                   number_of_samples / parameters.framerate))


def main() -> None:
    """
    A command line utility to silence the audio files in a given directory 
    Usage: python silence_audio.py --corpus <DEFAULT_DATA_DIRECTORY> [--silence_tier ]
    """

    global silence_mono
    global silence_stereo
    global do_not_publish

    parser = argparse.ArgumentParser(
        description="This script will silence a wave file based on annotations in an Elan tier")
    parser.add_argument('-c', '--corpus', help='Directory of audio and eaf files', type=str, required=True)
    parser.add_argument('-s', '--silence_tier', help='Silence audio when annotations are found on this tier', type=str,
                        default='Silence')
    parser.add_argument('-o', '--overwrite', help='Write over existing files', action="store_true")
    arguments = parser.parse_args()

    silence_mono = 0
    silence_stereo = [0, 0]
    suffix = 'S'

    '''
    Look for .eaf files, recursively from the passed arguments.corpus dir for file_path in 
    glob.iglob(arguments.corpus + '/**/*.eaf', recursive=True)
    '''
    
    for file_path in glob.iglob(arguments.corpus + '/*.eaf'):
        eaf_file = Eaf(file_path)
        names = eaf_file.get_tier_names()
        
        # Check for existence of silence tier
        if arguments.silence_tier in names:

            print("Have tier %s in %s" % (arguments.silence_tier, file_path))

            basename, extension = os.path.splitext(file_path)

            input = basename + ".wav"
            if arguments.overwrite:
                output = basename + ".wav"
            else:
                output = basename + suffix + ".wav"

            silence_audio(eaf_file, output)


if __name__ == "__main__":
    main()
