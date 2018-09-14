#!/usr/bin/python3.4
#
# python3.4 scripts/textgrid_to_json.py --input_dir input/data --output_dir input/output/tmp --output_json input/output/tmp/dirty.json
#
import os
import sys
import argparse
import json
from praatio import tgio
from typing import List, Dict, Union


def process_textgrid_file(input_dir: str) -> List[Dict[str, Union[str, int]]]:

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
    return int(seconds * 1000)


def write_json(output_json: str, intervals: List[Dict[str, Union[str, int]]]) -> None:
    with open(output_json, 'w') as outfile:
        json.dump(intervals, outfile, indent=4, separators=(',', ': '), sort_keys=False)


def main():

    """ Run the entire textgrid_to_json.py as a command line utility """

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
    
    write_json(output_json, intervals)

if __name__ == '__main__':
    main()