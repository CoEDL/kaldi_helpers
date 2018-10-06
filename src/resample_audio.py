#!/usr/bin/python

"""
Convert audio to 16 bit 16k mono WAV file

Usage: python3 resample_audio.py [--corpus <DEFAULT_DATA_DIRECTORY>] [--overwrite <true/false>]

@author Ola Olsson 2018
"""

import argparse
import glob
import os
import subprocess
import threading
from multiprocessing.dummy import Pool
from shutil import move
from src.utilities.file_utilities import find_files_by_extension
from typing import Tuple, Set
from functools import partial
from src.utilities.globals import *


def process_item(audio_file: Tuple[int, str], temporary_folders: str, process_lock, output_step: str) -> str:

    """
    Processes an audio file and resamples it to a 16k mono WAV file 
    
    :param audio_file: audio file to be resampled
    :return: name of the file to be resampled
    """

    input_index, input_audio_file = audio_file

    with process_lock:
        print("[%d, %d]%s" % (output_step, input_index, input_audio_file))
        output_step += 1

    # Extracting input directory names and file names
    input_directory, name = os.path.split(input_audio_file)
    base_name, extension = os.path.splitext(name)
    output_directory: str = os.path.join(input_directory, TEMPORARY_DIRECTORY)
    temporary_folders.add(output_directory)

    # Security check to avoid race conditions
    with process_lock:
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

    temporary_audio_name = join_normalised_path(output_directory, "%s.%s" % (base_name, "wav"))
    normalised_path = os.path.normpath(input_audio_file)
    if not os.path.exists(temporary_audio_name):
        command_line = [SOX_PATH, normalised_path, "-b", "16", "-c", "1",
                        "-r", "44.1k", "-t", "wav", temporary_audio_name]
        subprocess.call(command_line)

    return temporary_audio_name


def join_normalised_path(path1: str, path2: str):
    """
    Joining two paths by first normalising them and then re-normalising their concatenation.
    This allows for safer path conversions across various operating systems.
    
    :param path1: prepended part of the desired resulting path
    :param path2: appended part of the desired resulting path
    :return: concatenated and normalised path 
    """
    tmp = os.path.join(os.path.normpath(path1), os.path.normpath(path2))
    return os.path.normpath(tmp)


def main():

    """
    A command line utility to process the audio files in a given directory 
    Usage: python resample_audio.py [--corpus <DATA_DIRECTORY>] [--overwrite]
    """

    parser = argparse.ArgumentParser(
        description="This script will silence a wave file based on annotations in an Elan tier.")

    parser.add_argument("-c", "--corpus", help="Directory of audio and eaf files", type=str, default=DEFAULT_DATA_DIRECTORY)
    parser.add_argument("-o", "--overwrite", help="Write over existing files", action="store_true", default=True)

    args = parser.parse_args()
    overwrite = args.overwrite
    base_directory = args.corpus
    
    temporary_folders = set([])

    all_files_in_directory = set(glob.glob(os.path.join(base_directory, "**"), recursive=True))
    input_audio = find_files_by_extension(all_files_in_directory, set(AUDIO_EXTENSIONS))
    process_lock = threading.Lock()
    output_step = 0

    ''' Single-threaded solution '''
    # outputs = []
    # outputs.append(process_item(input_audio))

    ''' Multi-threaded solution '''
    with Pool() as p:
        temporary_folders = set([])
        outputs = p.map(partial(process_item, temporary_folders=temporary_folders,
                                process_lock=process_lock, output_step=output_step), enumerate(input_audio))
        if overwrite:
            # Replace original files
            for file in outputs:
                file_name = os.path.basename(file)
                parent = os.path.dirname(os.path.dirname(file))
                move(file, os.path.join(parent, file_name))
            # Perform clean up of temporary folders
            for file in temporary_folders:
                os.rmdir(file)
                continue


if __name__ == "__main__":
    main()

