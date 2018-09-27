#!/usr/bin/env python3

"""
Extracts transcription information and outputs them as json 
By default dumps json to ../input/output/tmp/dirty.json file
Usage: python3 textgrid_to_json.py --indir <input_file> [--output_dir output_directory] [--output_json output_file]
"""

import os
import sys
import argparse
import glob
import regex
import subprocess
from pyparsing import ParseException
from praatio import tgio
from typing import List, Dict, Union, Set
from src.utilities import *


def process_textgrid_files(input_directory: str) -> List[Dict[str, Union[str, int]]]:
    """
    Traverses through the textgrid files in the given directory and extracts 
    transcription information in each tier and creates a list of dictionaries,
    each containing data in the following format: 
                        {'audio_file_name': <file_name>,
                        'transcript': <transcription_label>,
                        'start_ms': <start_time_in_milliseconds>,
                        'stop_ms': <stop_time_in_milliseconds>}
                        
    :param input_directory: directory path containing input files from where the method
    :return: list of interval data in dictionary form
    """
    intervals: List[Dict[str, Union[str, int]]] = []

    for root, directories, files in os.walk(input_directory):
        for filename in files:
            basename, extension = os.path.splitext(filename)
            if filename.endswith(".TextGrid"):
                text_grid: tgio.Textgrid = tgio.openTextgrid(os.path.join(root, filename))
                speech_tier: tgio.IntervalTier = text_grid.tierDict["Speech"]
                for start, stop, label in speech_tier.entryList:
                    label_word: str = label.replace('"', '')
                    intervals.append({
                        "audio_file_name": os.path.join(".", basename + ".wav"),
                        "transcript": label_word,
                        "start_ms": second_to_milli(float(start)),
                        "stop_ms": second_to_milli(float(stop))
                    })

    return intervals


def second_to_milli(seconds: float) -> int:
    """
    Converts from seconds to milliseconds 
    
    :param seconds: time in seconds
    :return: converted time rounded to nearest millisecond
    """

    return int(seconds * 1000)


def main() -> None:

    """ 
    Run the entire textgrid_to_json.py as a command line utility 
    Usage: python3 textgrid_to_json.py --indir <input_file> [--output_dir output_directory] [--output_json output_file]
    """

    parser = argparse.ArgumentParser(
        description = "Search input folder for .TextGrid files and convert to JSON on stdout")
    parser.add_argument("-i", "--input_dir", help="The input data dir", type=str, default="input/data/")
    parser.add_argument("-o", "--output_dir", help="Output directory", type=str, default=".") #default="input/output/tmp"
    args = parser.parse_args()

    try:
        input_directory = args.input_dir
        output_directory = input_directory if args.output_dir == "." else args.output_dir
    except ParseException:
        parser.print_help()
        sys.exit(0)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    intervals = process_textgrid_files(input_directory)

    result_base_name, name = os.path.split(output_directory)
    if not name or name == '.':
        outfile_name = "intervals.json"
    else:
        outfile_name = os.path.join(name + '.json')
    output_json = os.path.join(result_base_name, outfile_name)

    write_data_to_json_file(intervals, output_json)

if __name__ == '__main__':
    main()