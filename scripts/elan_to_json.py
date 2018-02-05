#!/usr/bin/python3

# get all files in the repositoy
# can use recursive atm as long as we don't need numpy
# pass in corpus path
# throw an error if matching file wav isn't found in the corpus dir

import argparse
import glob
import json
import sys
import os
from pympi.Elan import Eaf

parser = argparse.ArgumentParser(description="This script will slice audio and output text in a format ready for our Kaldi pipeline.")
parser.add_argument('-i', '--input_dir', help='Directory of dirty audio and eaf files', type=str, default='input/data/')
parser.add_argument('-o', '--output_dir', help='Output directory', type=str, default='../input/output/tmp/')
parser.add_argument('-t', '--tier', help='Target language tier name', type=str, default='Phrase')
parser.add_argument('-j', '--output_json', help='File name to output json', type=str, default='../input/output/tmp/dirty.json')
args = parser.parse_args()
try:
    input_dir = args.input_dir
    output_dir = args.output_dir
    tier = args.tier
    output_json = args.output_json
except Exception:
    parser.print_help()
    sys.exit(0)

# print(input_dir, file=sys.stderr)
# print(output_dir, file=sys.stderr)
# print(tier, file=sys.stderr)

annotations_data = []

# Build output dier if needed
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def findFilesByExt(setOfAllFiles, exts):
    res = []
    for f in setOfAllFiles:
        name, ext = os.path.splitext(f)
        if ("*" + ext.lower()) in exts:
            res.append(f)
    return res


def write_json():
    with open(output_json, 'w') as outfile:
        json.dump(annotations_data, outfile, indent=4, separators=(',', ': '), sort_keys=False)


def read_eaf(ie):
    # Get paths to files
    inDir, name = os.path.split(ie)
    basename, ext = os.path.splitext(name)

    input_eaf = Eaf(ie)

    # I want the media in the same folder as the eaf. error if not found
    # We could also parse the linked media.. let try this later
    # files = input_eaf.get_linked_files()

    # look for wav file matching the eaf file
    if os.path.isfile(os.path.join(inDir, basename + ".wav")):
        print("WAV file found for " + basename, file=sys.stderr)
    else:
        raise ValueError('Eeeek! WAV file not found for ' + basename + '. Please put it next to the eaf file in ' + inDir)

    # Get annotations and params (thigs like speaker id) on the target tier
    annotations = sorted(input_eaf.get_annotation_data_for_tier(tier))
    params = input_eaf.get_parameters_for_tier(tier)
    if 'PARTICIPANT' in params:
        speaker_id = params['PARTICIPANT']

    for ann in annotations:
        start = ann[0]
        end = ann[1]
        annotation = ann[2]

        # print('processing annotation: ' + annotation, start, end)
        obj = {
            'audioFileName': os.path.join(".", basename + ".wav"),
            'transcript': annotation,
            'startMs': start,
            'stopMs': end
        }
        if 'PARTICIPANT' in params:
            obj["speakerId"] = speaker_id
        annotations_data.append(obj)


g_exts = ["*.eaf"]
allFilesInDir = set(glob.glob(os.path.join(input_dir, "**"), recursive=True))
input_eafs = findFilesByExt(allFilesInDir, set(g_exts))


for ie in input_eafs:
    read_eaf(ie)

write_json()
