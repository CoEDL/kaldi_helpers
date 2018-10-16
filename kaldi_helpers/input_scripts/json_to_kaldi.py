#!/usr/local/bin/python

"""
Parse json file and extract transcription information which are then processed and output_scripts in the desired Kaldi format.
The output_scripts files will be stored in two separate folders training and testing inside the specified output_scripts directory.

training : 
    corpus.txt, text, segments, wav.scp, utt2spk, spk2utt
testing : 
    corpus.txt, text, segments, wav.scp, utt2spk, spk2utt
            
The training folder is for the model creation using Kaldi, whereas the testing folder is used for verifying the 
reliability of the model.
            
Usage: python3 json_to_kaldi.py [-h] -i INPUT_JSON [-o OUTPUT_FOLDER] [-s]
"""

import argparse
import json
import os
import sys
import uuid
import shutil
import subprocess
from pyparsing import ParseException
from typing import Set, List, Tuple, Dict
from kaldi_helpers.script_utilities import *


class KaldiInput:

    """
    Class to store information for the training and testing data sets.     
    """

    def __init__(self, output_folder: str) -> None:

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self.speakers: Dict[str, str] = {}
        self.recordings: Dict[str, str] = {}
        self.utterances: Dict[str, str] = {}

        self.segments_list: List[str] = []
        self.transcripts_list: List[str] = []
        self.speakers_list: List[str] = []
        self.recordings_list: List[str] = []
        self.utt2spk_list: List[str] = []
        self.corpus_list: List[str] = []

        self.segments_file: TextIOWrapper = open(output_folder + "/segments", "w", encoding="utf-8")
        self.transcripts_file: TextIOWrapper = open(output_folder + "/text", "w", encoding="utf-8")
        self.speakers_file: TextIOWrapper = open(output_folder + "/spk2gender", "w", encoding="utf-8")
        self.recordings_file: TextIOWrapper = open(output_folder + "/wav.scp", "w", encoding="utf-8")
        self.utt2spk_file: TextIOWrapper = open(output_folder + "/utt2spk", "w", encoding="utf-8")
        self.corpus_file: TextIOWrapper = open(output_folder + "/corpus.txt", "w", encoding="utf-8")

    def add_speaker(self, speaker_id: str) -> str:
        """
        Adds a speaker element if it is not already present.
        
        :param speaker_id: speaker id - could be a name of a uuid code
        :return: returns the correctly formatted speaker id 
        """
        if speaker_id not in self.speakers:
            self.speakers[speaker_id] = str(uuid.uuid4()) # create speaker id
            self.speakers_list.append(self.speakers[speaker_id] + " " + "f\n") # writing gender
        return self.speakers[speaker_id]

    def add_recording(self, audio_file: str) -> str:
        """
        Adds an audio file it is not already present.
        
        :param audio_file: name of audio file 
        :return: returns a correctly formatted audio file description
        """
        if audio_file not in self.recordings:
            self.recordings[audio_file] = str(uuid.uuid4()) # create recording id
            self.recordings_list.append(self.recordings[audio_file] + " " + WAV_FOLDER + audio_file + "\n")
        return self.recordings[audio_file]

    def add(self, recording_id: str, speaker_id: str, utterance_id: str,
            start_ms: int, stop_ms: int, transcript: str, silence_markers: bool) -> None:
        """
        Appends new items to the transcripts, segments, utt2spk and corpus lists.
        
        :param recording_id: id for the recording file
        :param speaker_id: id for the speaker who uttered the phrase
        :param utterance_id: unique id for the uttered phrase
        :param start_ms: start of the uttered phrase
        :param stop_ms: stop time of the uttered phrase
        :param transcript: the uttered phrase
        :param silence_markers: boolean condition indicating whether to include silence markers
        
        :return: 
        """
        if silence_markers:
            self.transcripts_list.append(utterance_id + " !SIL " + transcript + " !SIL\n")
        else:
            self.transcripts_list.append(utterance_id + " " + transcript + "\n")
        self.segments_list.append(utterance_id + " " + recording_id + " " + f"{start_ms/1000.0} {stop_ms/1000.0}\n")
        self.utt2spk_list.append(utterance_id + " " + speaker_id + "\n")
        self.corpus_list.append(transcript + "\n")

    def write_and_close(self) -> None:

        """
        After parsing the json file and populating the segments, transcripts, speakers, recordings, utt2spk and corpus 
        lists with data, this function performs the final write to their respective files. 
        
        :return: 
        """

        self.segments_list.sort()
        self.segments_file.write("".join(self.segments_list))
        self.segments_file.close()

        self.transcripts_list.sort()
        self.transcripts_file.write("".join(self.transcripts_list))
        self.transcripts_file.close()

        self.speakers_list.sort()
        self.speakers_file.write("".join(self.speakers_list))
        self.speakers_file.close()

        self.recordings_list.sort()
        self.recordings_file.write("".join(self.recordings_list))
        self.recordings_file.close()

        self.utt2spk_list.sort()
        self.utt2spk_file.write("".join(self.utt2spk_list))
        self.utt2spk_file.close()

        self.corpus_list.sort()
        self.corpus_file.write("".join(self.corpus_list))
        self.corpus_file.close()


def main() -> None:

    """ 
    Run the entire json_to_kaldi.py as a command line utility. 
    
    Usage: python3 json_to_kaldi.py [-h] -i INPUT_JSON [-o OUTPUT_FOLDER] [-s]
    """
    parser = argparse.ArgumentParser(description="Convert json from stdin to Kaldi input_scripts files (in output_scripts-folder).")
    parser.add_argument("-i", "--input_json", type=str, help="The input_scripts json file", required=False,
                        default=os.path.join(".", "test", "testfiles", "example.json"))
    parser.add_argument("-o", "--output_folder", type=str, help="The output_scripts folder", default=os.path.join(".", "data"))
    parser.add_argument("-s", "--silence_markers", action="store_true", help="The input_scripts json file")
    arguments: argparse.Namespace = parser.parse_args()

    if not os.path.isfile(arguments.input_json):
        sys.exit(1);

    try:
        input_file: TextIOWrapper = open(arguments.input_json, "r")
        json_transcripts: str = json.loads(input_file.read())
        input_file.close()
    except FileNotFoundError:
        print(f"JSON file could not be found: {arguments.input_json}")
    except:
        print("Unexpected error", sys.exc_info()[0])
        raise

    if not os.path.exists(arguments.output_folder):
        os.makedirs(arguments.output_folder)

    testing_input: KaldiInput = KaldiInput(arguments.output_folder + "/testing")
    training_input: KaldiInput = KaldiInput(arguments.output_folder + "/training")

    for i, json_transcript in enumerate(json_transcripts):
        transcript: str = json_transcript.get("transcript", "")
        start_ms: int = json_transcript.get("start_ms", 0)
        stop_ms: int = json_transcript.get("stop_ms", 0)

        # Speaker ID is not available in textgrid files
        if "speaker_id" in json_transcript:
            speaker_id: str = json_transcript.get("speaker_id", "")
        else:
            speaker_id: str = str(uuid.uuid4())

        audio_file: str = json_transcript.get("audio_file_name", "").replace("\\", "/")

        # 10% of the data set is stored away for use as testing data, other 90% is training data
        if i % 10 == 0:

            speaker_id = testing_input.add_speaker(speaker_id) # add speaker_id
            recording_id: str = testing_input.add_recording(audio_file) # add audio file name
            utterance_id: str = speaker_id + "-" + str(uuid.uuid4()) # add utterance id
            #silence_markers: bool = False
            testing_input.add(recording_id,
                              speaker_id,
                              utterance_id,
                              start_ms,
                              stop_ms,
                              transcript,
                              arguments.silence_markers)

        else:

            speaker_id = training_input.add_speaker(speaker_id) # add speaker id
            recording_id: str = training_input.add_recording(audio_file) # add audio file name
            utterance_id: str = speaker_id + "-" + str(uuid.uuid4()) # add utterance id
            #silence_markers: bool = True
            training_input.add(recording_id,
                               speaker_id,
                               utterance_id,
                               start_ms,
                               stop_ms,
                               transcript,
                               arguments.silence_markers)

    testing_input.write_and_close()
    training_input.write_and_close()

if __name__ == "__main__":
    main()
