#!/usr/bin/env python3

"""
Extracts transcription information and outputs them as json 
By default dumps json to ../input/output/tmp/dirty.json file
Usage: python3 textgrid_to_json.py --indir <input_file> [--output_dir output_directory] [--output_json output_file]
"""

import os
import sys
import argparse
from praatio import tgio
from typing import List, Dict, Union
from src.utilities import write_data_to_json_file


def process_textgrid_file(input_dir: str) -> List[Dict[str, Union[str, int]]]:
    """
    Traverses through the textgrid file and extracts transcription information
    in each tier and creates a list of dictionaries, each containing data in the
    following format: {'audioFileName': <file_name>,
                        'transcript': <transcription_label>,
                        'startMs': <start_time_in_milliseconds>,
                        'stopMs': <stop_time_in_milliseconds>}
                        
    :param input_dir: directory path containing input files from where the method
                    
    :return: list of interval data in dictionary form
    """
    intervals = []

    for (root, dirs, files) in os.walk(input_dir):
        for filename in files:
            basename, ext = os.path.splitext(filename)
            if filename.endswith(".TextGrid"):
                tg = tgio.openTextgrid(os.path.join(root, filename))
                speech_tier = tg.tierDict['Speech']
                for start, stop, label in speech_tier.entryList:
                    label_w = label.replace('"', '')

                    obj = {
                        'audioFileName': os.path.join(".", basename + ".wav"),
                        'transcript': label_w,
                        'startMs': sec_to_milli(float(start)),
                        'stopMs': sec_to_milli(float(stop))
                    }

                    intervals.append(obj)

    return intervals


def sec_to_milli(seconds: float) -> int:
    """
    Converts from seconds to milliseconds 
    
    :param seconds: time in seconds
    :return: converted time rounded to nearest millisecond
    """

    return int(seconds * 1000)


def main():

    """ 
    Run the entire textgrid_to_json.py as a command line utility 
    Usage: python3 textgrid_to_json.py --indir <input_file> [--output_dir output_directory] [--output_json output_file]
    """

    parser = argparse.ArgumentParser(
        description='Search input-folder for .TextGrid files and convert to JSON on stdout')
    parser.add_argument('-i', '--input_dir', help='The input data dir', type=str, default='input/data/')
    parser.add_argument('-o', '--output_dir', help='Output directory', type=str, default='input/output/tmp/')
    parser.add_argument('-j', '--output_json', help='File name to output json', type=str,
                        default='input/output/tmp/dirty.json')
    args = parser.parse_args()
    try:
        input_dir = args.input_dir
        output_dir = args.output_dir
        output_json = args.output_json
    except Exception:
        parser.print_help()
        sys.exit(0)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    intervals = process_textgrid_file(input_dir)

    write_data_to_json_file(intervals, output_json)

if __name__ == '__main__':
    main()