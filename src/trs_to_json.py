#!/usr/bin/python3

"""
Parse trs file and extract information from it for json
Dumps json to sys stdout,
so you'll need to direct the output to a file when running the script
Usage: python3 trs_to_json.py --indir ../input/data > ../input/output/tmp/dirty.json
"""

import xml.etree.ElementTree as ET
import glob
import sys
import os
import argparse
import json
import platform
import uuid
from typing import List, Dict, Union
from src.utilities import find_files_by_extension


def find_first_file_by_extension(set_of_all_files: List[str], extensions: List[str]) -> str:
    """
    Searches for the first file with a given extension in a set of files.
    
    :param set_of_all_files: set of file names in string format
    :param extensions: file extension being searched for
    :return: name of the first file_name that is matched, if any. otherwise, this method returns an empty string
    """
    for f in set_of_all_files:
        name, extension = os.path.splitext(f)
        if ("*" + extension.lower()) in extensions:
            return f
    return ""


def conditional_log(cond: bool, text: str) -> None:
    """
    Work around for UTF8 file name and the windows console.
    :param cond: condition to indicate whether text should be output to stderr
    :param text: text to output to stderr 
    """

    if cond:
        # Super-annoying mumbojumbo to work around utf8 file name and the windows console which under the debugger
        # claims to be utf8 but then fails regardless!
        if platform.system() == 'Windows':
            sys.stderr.write(text.encode('cp850', errors='backslashreplace').decode(sys.stdout.encoding))
        else:
            sys.stderr.write(text)
        sys.stderr.flush()


def process_trs_file(file_name: str, g_verbose_output: bool) -> List[Dict[str, Union[str, float]]]:

    """
    Method to process the .trs files and returns a list of utterances.
    :param file_name: file_name of the .trs file
    :param g_verbose_output: whether or not output to stdout
    :return: a list of dictionaries. each dictionary contains key information on utterances, including 
            speaker_ID, audiofile_name, transcript, startMs, stopMs.
    """

    conditional_log(g_verbose_output, "Processing transcript '%s'\n" % file_name)

    utterances: List[Dict[str, Union[str, float]]] = []
    try:
        tree = ET.parse(file_name) # loads an external XML section into this element tree
        root = tree.getroot() # root of element tree
        wave_name = root.attrib['audio_filename'] + ".wav" # changed audio_file_name to audio_filename
        turn_nodes = tree.findall(".//Turn")
        for turn_node in turn_nodes:
            utterances = utterances + process_turn(file_name, turn_node, wave_name, tree)

    except ET.ParseError as err:
        conditional_log(True, "XML parser failed to parse '%s'!\n" % file_name)
        conditional_log(True, str(err))

    return utterances


def process_turn(file_name, turn_node, wave_name, tree):
    """
    Helper method to process each turn_node in the .trs file
    :param file_name: name of the file
    :param turn_node: name of the turn node to be processed
    :param wave_name: name of .wav audio file to be processed
    :param tree: XML data represented as a tree data structure
    :return: list of key information on utterances
    """

    # turn_start = float(turn_node.attrib['start_time'])
    turn_end = float(turn_node.attrib['endTime']) # changed end_time to endTime
    speaker_ID = turn_node.get('speaker', '')

    speaker_name_node = tree.find(".//Speaker[@id='%s']" % speaker_ID)
    speaker_name = ""
    if speaker_name_node is not None:
        speaker_name = speaker_name_node.attrib['name']
    else:
        speaker_name = str(uuid.uuid4())
    items = [(ch.attrib['time'], ch.tail.strip()) for ch in turn_node.findall("./Sync")]

    base_dir, name = os.path.split(file_name)
    base_name, _ = os.path.splitext(name)
    # wavefile_name = os.path.join(base_dir, wave_name)
    wavefile_name = os.path.join(".", wave_name)

    result = []

    for i in range(0, len(items)):
        time_str, trans_str = items[i]
        start_time = float(time_str)
        if i < len(items) - 1:
            time_str2, _ = items[i + 1]
            end_time = float(time_str2)
        else:
            end_time = turn_end
        result.append({"speaker_ID": speaker_name,
                       "audiofile_name": wavefile_name,
                       "transcript": trans_str,
                       "startMs": start_time * 1000.0,
                       "stopMs": end_time * 1000.0})
        start_time = end_time

    return result


def main():

    """ Run the entire trs_to_json.py as a command line utility """
    # utterances = process_trs_file("..\\test\\testfiles\\exampleTranscription.trs", True)
    # print(utterances)

    parser = argparse.ArgumentParser(description='A command line utility to convert .trs files to .json',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d', '--indir', dest='inputDir', help='Input directory, default=\'.\'', default='.')
    parser.add_argument('-v', '--verbose', dest='verbose', help='More logging to console.', action="store_true")

    args = parser.parse_args()

    g_base_dir = args.inputDir
    g_verbose_output = args.verbose

    if g_verbose_output:
        sys.stderr.write(g_base_dir + "\n")

    all_files_in_dir = list(glob.glob(os.path.join(g_base_dir, "**"), recursive=True))

    transcript_names = find_files_by_extension(all_files_in_dir, list(["*.trs"]))

    # iterate through all .trs files and process them, creates audio clip files and returns the set
    # {file_name, transcriptString, speaker_ID}
    utterances = []
    for fn in transcript_names:
        utterances = utterances + process_trs_file(fn, g_verbose_output)

    result_base_name, name = os.path.split(g_base_dir)

    if name == '.':
        outfile_name = "utterances.json"
    else:
        outfile_name = name + ".json"

    with open(outfile_name, 'w') as outfile:
        # outfile = sys.stdout
        json.dump(utterances, outfile, indent=2)


if __name__ == '__main__':
    main()
