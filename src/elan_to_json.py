#!/usr/bin/python3

"""
Get all files in the repository
can use recursive atm as long as we don't need numpy
pass in corpus path
throw an error if matching file wav isn"t found in the corpus directory
"""

import glob
import sys
import os
from argparse import ArgumentParser
from pympi.Elan import Eaf
from typing import List
from src.utilities import find_files_by_extension
from src.utilities import write_data_to_json_file


def read_eaf(input_elan_file, tier_name: str) -> List[dict]:
    # Get paths to files
    input_directory, full_file_name = os.path.split(input_elan_file)
    file_name, extension = os.path.splitext(full_file_name)

    input_eaf = Eaf(input_elan_file)

    # Look for wav file matching the eaf file in same directory
    if os.path.isfile(os.path.join(input_directory, file_name + ".wav")):
        print("WAV file found for " + file_name, file=sys.stderr)
    else:
        raise ValueError(f"WAV file not found for {full_file_name}. "
                         f"Please put it next to the eaf file in {input_directory}.")

    # Get annotations and parameters (things like speaker id) on the target tier
    annotations = sorted(input_eaf.get_annotation_data_for_tier(tier_name))
    parameters = input_eaf.get_parameters_for_tier(tier_name)
    speaker_id = parameters.get("PARTICIPANT", default="")

    annotations_data = []

    for annotation in annotations:
        start = annotation[0]
        end = annotation[1]
        annotation = annotation[2]

        # print("processing annotation: " + annotation, start, end)
        obj = {
            "audioFileName": f"{file_name}.wav",
            "transcript": annotation,
            "startMs": start,
            "stopMs": end
        }
        if "PARTICIPANT" in parameters:
            obj["speakerId"] = speaker_id
        annotations_data.append(obj)

    return annotations_data


def create_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(description="This script takes an directory with ELAN files and "
                                        "slices the audio and output text in a format ready "
                                        "for our Kaldi pipeline.")
    parser.add_argument("-i", "--input_dir",
                        help="Directory of dirty audio and eaf files",
                        type=str,
                        default="input/data/")
    parser.add_argument("-o", "--output_dir",
                        help="Output directory",
                        type=str,
                        default="../input/output/tmp/")
    parser.add_argument("-t", "--tier",
                        help="Target language tier name",
                        type=str,
                        default="Phrase")
    parser.add_argument("-j", "--output_json",
                        help="File name to output json",
                        type=str,
                        default="../input/output/tmp/dirty.json")
    return parser


def main():
    """ Run the entire elan_to_json.py as a command line utility """
    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        input_dir = args.input_dir
        output_dir = args.output_dir
        tier = args.tier
        output_json = args.output_json
    except Exception:
        parser.print_help()
        sys.exit(0)

    # Build output directory if needed
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    all_files_in_directory = set(glob.glob(os.path.join(input_dir, "**"), recursive=True))
    input_eafs_files = find_files_by_extension(all_files_in_directory, {"*.eaf"})

    annotations_data = []

    for input_eaf_file in input_eafs_files:
        annotations_data.extend(read_eaf(input_eaf_file, tier))

    write_data_to_json_file(annotations_data, output_json)


if __name__ == "__main__":
    main()

