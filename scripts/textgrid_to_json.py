#!/usr/bin/python3.4
#
# python3.4 scripts/textgrid_to_json.py --input_dir input/data --output_dir input/output/tmp --output_json input/output/tmp/dirty.json
#
import os
import sys
import argparse
import json
from praatio import tgio


parser = argparse.ArgumentParser(description='Search input-folder for .TextGrid files and convert to JSON on stdout')
parser.add_argument('-i', '--input_dir', help='The input data dir', type=str, default='input/data/')
parser.add_argument('-o', '--output_dir', help='Output directory', type=str, default='input/output/tmp/')
parser.add_argument('-j', '--output_json', help='File name to output json', type=str, default='input/output/tmp/dirty.json')
args = parser.parse_args()
try:
    input_dir = args.input_dir
    output_dir = args.output_dir
    output_json = args.output_json
except Exception:
    parser.print_help()
    sys.exit(0)

# Build output dier if needed
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def sec2milli(seconds):
    return int(seconds * 1000)


def write_json():
    with open(output_json, 'w') as outfile:
        json.dump(intervals, outfile, indent=4, separators=(',', ': '), sort_keys=False)


intervals = []

for (root, dirs, files) in os.walk(input_dir):
    for filename in files:
        basename, ext = os.path.splitext(filename)

        if filename.endswith(".TextGrid"):
            tg = tgio.openTextgrid(os.path.join(root, filename))
            speechTier = tg.tierDict['Speech']
            for start, stop, label in speechTier.entryList:
                # Should pass in a name to get, for now use Speech
                label_w = label.replace('"', '')

                obj = {
                    'audioFileName': os.path.join(".", basename + ".wav"),
                    'transcript': label_w,
                    'startMs': sec2milli(float(start)),
                    'stopMs': sec2milli(float(stop))
                }
                intervals.append(obj)

            # print("doing file " + filename, file=sys.stderr)
            # intervals.extend(extract_textgrid_intervals(filename))

write_json()
# write_json(intervals)
