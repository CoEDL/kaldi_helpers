#!/usr/bin/env python3

"""
Parse trs file and extract information from it for json
Dumps json to sys stdout,
so you'll need to direct the output_scripts to a file when running the script

Usage: python3 trs_to_json.py [-h] [-d INPUT_DIRECTORY] [-v] > {OUTPUT_FILE]
"""

import xml.etree.ElementTree as ET
import glob
import sys
import os
import argparse
import json
import platform
import uuid
import subprocess
import regex
from pyparsing import ParseException
from typing import List, Dict, Union, Set, Tuple
from kaldi_helpers.script_utilities import *


def conditional_log(condition: bool, text: str) -> None:
    """
    Work around for UTF8 file name and the windows console.
    
    :param condition: condition to indicate whether text should be output_scripts to stderr
    :param text: text to output_scripts to stderr
    """

    if condition:
        if platform.system() == "Windows":
            sys.stderr.write(text.encode("cp850", errors="backslashreplace").decode(sys.stdout.encoding))
        else:
            sys.stderr.write(text)
        sys.stderr.flush()


def process_trs(file_name: str, verbose_output: bool) -> List[Dict[str, Union[str, float]]]:

    """
    Method to process the trs files and return a list of utterances.
    
    :param file_name: file_name of the .trs file
    :param verbose_output: whether or not output_scripts to stderr
    :return: a list of dictionaries. each dictionary contains key information on utterances in the following format:
                                     {'speaker_id': <speaker_id>,
                                    'audio_file_name': <file_name>,
                                    'transcript': <transcription_label>,
                                    'start_ms': <start_time_in_milliseconds>,
                                    'stop_ms': <stop_time_in_milliseconds>}
    """

    conditional_log(verbose_output, "Processing transcript '%s'\n" % file_name)

    utterances: List[Dict[str, Union[str, float]]] = []
    try:
        tree: ET.ElementTree = ET.parse(file_name)
        root: ET.Element = tree.getroot()
        wave_name: str = root.attrib["audio_filename"] + ".wav"
        turn_nodes: List[ET.Element] = tree.findall(".//Turn")

        for turn_node in turn_nodes:
            utterances = utterances + process_turn(wave_name, turn_node, tree)

    except ET.ParseError as error:
        conditional_log(True, "XML parser failed to parse '%s'!\n" % file_name)
        conditional_log(True, str(error))

    return utterances


def process_turn(wave_name: str, turn_node: ET.Element, tree: ET.ElementTree) -> List[Dict[str, Union[str, float]]]:
    """
    Helper method to process each turn_node in the .trs file.
    
    :param file_name: name of the file
    :param turn_node: the ElementTree node to be processed
    :param wave_name: name of .wav audio file to be processed
    :param tree: XML data represented as a tree data structure
    :return: list of key information on utterances
    """

    turn_end: float = float(turn_node.attrib["endTime"])
    speaker_id: str = turn_node.get("speaker", "")

    speaker_name_node: ET.Element = tree.find(".//Speaker[@id='%s']" % speaker_id)
    if speaker_name_node is not None:
        speaker_name: str = speaker_name_node.attrib["name"]
    else:
        speaker_name: str = str(uuid.uuid4())

    items: List[Tuple[str, str]] = [(element.attrib["time"], element.tail.strip()) for element in turn_node.findall("./Sync")]
    wave_file_name = os.path.join(".", wave_name)

    result: List[Dict[str, Union[str, float]]] = []

    for i in range(0, len(items)):
        time_str, transcription_str = items[i]
        start_time: float = float(time_str)
        if i < len(items) - 1:
            end_time: float = float(items[i + 1][0])
        else:
            end_time = turn_end
        result.append({"speaker_id": speaker_name,
                       "audio_file_name": wave_file_name,
                       "transcript": transcription_str,
                       "start_ms": start_time * 1000.0,
                       "stop_ms": end_time * 1000.0})

    return result


def main() -> None:

    """ 
    Run the entire trs_to_json.py as a command line utility. It processes the utterances 
    and outputs to a file in the same directory as the input_scripts .trs file. The output_scripts files
    is named after the basename of the input_scripts directory appended with a .json extension.
    
    Usage: python3 trs_to_json.py [-h] [-d INPUT_DIRECTORY] [-v] > {OUTPUT_FILE]
    """

    parser = argparse.ArgumentParser(description="A command line utility to convert .trs files to .json",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--input_dir", dest="input_directory", help="Input directory, default='.'", default=".")
    parser.add_argument('-v', '--verbose', dest='verbose', help='More logging to console.', action="store_true")
    arguments: argparse.Namespace = parser.parse_args()

    if arguments.verbose:
        sys.stderr.write(arguments.input_directory + "\n")

    all_files_in_dir: List[str] = list(glob.glob(os.path.join(arguments.input_directory, "**"), recursive=True))
    transcript_names: Set[str] = find_files_by_extension(all_files_in_dir, list(["*.trs"]))

    utterances = []
    for file_name in transcript_names:
        utterances = utterances + process_trs(file_name, arguments.verbose)

    result_base_name, name = os.path.split(arguments.input_directory)
    if not name or name == '.':
        outfile_name = "utterances.json"
    else:
        outfile_name = os.path.join(name + '.json')

    outfile_path = os.path.join(arguments.input_directory, outfile_name)
    write_data_to_json_file(utterances, outfile_path)

if __name__ == '__main__':
    main()
