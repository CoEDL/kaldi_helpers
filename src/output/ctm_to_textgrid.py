#!/usr/bin/python

"""
# Copyright 2018 The University of Queensland (Author: Nicholas Lambourne)
# LICENCE: MIT
"""

from argparse import ArgumentParser
from csv import reader
from pathlib import Path
from typing import Dict
from praatio import tgio


def ctm_to_dictionary(file_name: str) -> dict:
    with open(file_name, "r") as file:
        ctm_entries = list(reader(file, delimiter=" "))
    textgrid_dictionary = dict()
    for entry in ctm_entries:
        utterance_id = entry[0]
        if utterance_id not in textgrid_dictionary:
            textgrid_dictionary[utterance_id] = []
        utterance_segment = (entry[2],                                # Start time
                             str(float(entry[2]) + float(entry[3])),  # End time (start + duration)
                             entry[4])                                # Inferred text
        textgrid_dictionary[utterance_id].append(utterance_segment)
    return textgrid_dictionary


def wav_scp_to_dictionary(scp_file_name: str) -> dict:
    wav_dictionary = dict()
    with open(scp_file_name) as file:
        wav_entries = list(reader(file, delimiter=" "))
        for entry in wav_entries:
            utterance_id = entry[0]
            wav_file_path = entry[1]
            wav_dictionary[utterance_id] = wav_file_path
    return wav_dictionary


def create_textgrid(wav_dictionary: Dict[str, str],
                    ctm_dictionary: dict,
                    output_directory: str) -> None:
    for index, utterance_id in enumerate(wav_dictionary.keys()):
        textgrid = tgio.Textgrid()
        tier = tgio.IntervalTier(name='phones',
                                 entryList=ctm_dictionary[utterance_id],
                                 minT=0,
                                 pairedWav=wav_dictionary[utterance_id])
        textgrid.addTier(tier)
        textgrid.save(output_directory.join(f"utterance-{index}.TextGrid"))


def main() -> None:
    parser: ArgumentParser = ArgumentParser(description="Converts Kaldi CTM format to Praat Textgrid Format.")
    parser.add_argument("--ctm", type=str, help="The input CTM format file", required=True)
    parser.add_argument("--wav", type=str, help="The input wav.scp file", required=True)
    parser.add_argument("--outdir", type=str, help="The directory path for the Praat TextGrid output",
                        default=".")
    arguments = parser.parse_args()

    ctm_dictionary = ctm_to_dictionary(arguments.ctm)
    wav_dictionary = wav_scp_to_dictionary(arguments.wav)
    output_directory = Path(arguments.outdir)

    if not output_directory.parent:
        Path.mkdir(output_directory.parent, parents=True)

    create_textgrid(wav_dictionary,
                    ctm_dictionary,
                    output_directory)


if __name__ == '__main__':
    main()
