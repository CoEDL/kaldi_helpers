#!/usr/local/bin/python3

import argparse
import json
import os
import sys
import uuid

parser = argparse.ArgumentParser(description='Convert json from stdin to Kaldi input files (in output-folder).')
parser.add_argument('--output-folder', type=str, required=True, help='The output folder')
parser.add_argument('--no-silence-markers', action="store_true", help='The input json file')
args = parser.parse_args()

# input_json_fname = args.input_json
output_folder = args.output_folder
silence_markers = not args.no_silence_markers


# f_in = open(input_json_fname, "r")
f_in = sys.stdin

json_transcripts = json.loads(f_in.read())
f_in.close()

speakers = {}
recordings = {}
utterances = {}

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

l_segments, l_transcripts, l_speakers, l_recordings, l_utt2spk, l_corpus = [], [], [], [], [], []

f_segments = open(output_folder + "/segments", "w", encoding="utf-8")
f_transcripts = open(output_folder + "/text", "w", encoding="utf-8")
f_speakers = open(output_folder + "/spk2gender", "w", encoding="utf-8")
f_recordings = open(output_folder + "/wav.scp", "w", encoding="utf-8")
f_utt2spk = open(output_folder + "/utt2spk", "w", encoding="utf-8")
f_corpus = open(output_folder + "/corpus.txt", "w", encoding="utf-8")


for json_transcript in json_transcripts:
    transcript = json_transcript["transcript"]
    startMs = json_transcript["startMs"]
    stopMs = json_transcript["stopMs"]

    if "speakerId" in json_transcript:
        speakerId = json_transcript["speakerId"]
    else:
        speakerId = str(uuid.uuid4())

    audioFileName = json_transcript["audioFileName"].replace("\\", "/")

    if speakerId not in speakers:
        # create speaker id
        speakers[speakerId] = str(uuid.uuid4())
        # writing gender
        l_speakers.append(speakers[speakerId] + " " + "f\n")

    if audioFileName not in recordings:
        # create recording id
        recordings[audioFileName] = str(uuid.uuid4())
        l_recordings.append(recordings[audioFileName] + " " + audioFileName + "\n")

    speaker_id = speakers[speakerId]
    recording_id = recordings[audioFileName]
    utterance_id = speakers[speakerId] + "-" + str(uuid.uuid4())

    if silence_markers:
        l_transcripts.append(utterance_id + " !SIL " + transcript + " !SIL\n")
    else:
        l_transcripts.append(utterance_id + " " + transcript + "\n")
    l_segments.append(utterance_id + " " + recording_id + " " + "%f %f\n" % (startMs / 1000.0, stopMs / 1000.0))
    # f_utt2spk.write(utterance_id + " " + speaker_id + "\n")
    # hack to match utterances to utterances
    l_utt2spk.append(utterance_id + " " + utterance_id + "\n")
    l_corpus.append(transcript + "\n")


l_segments.sort()
f_segments.write("".join(l_segments))
f_segments.close()

l_transcripts.sort()
f_transcripts.write("".join(l_transcripts))
f_transcripts.close()

l_speakers.sort()
f_speakers.write("".join(l_speakers))
f_speakers.close()

l_recordings.sort()
f_recordings.write("".join(l_recordings))
f_recordings.close()

l_utt2spk.sort()
f_utt2spk.write("".join(l_utt2spk))
f_utt2spk.close()

l_corpus.sort()
f_corpus.write("".join(l_corpus))
f_corpus.close()
