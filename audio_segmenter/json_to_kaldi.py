import json;
import sys;
import uuid;
import os;
import sys;

import argparse

parser = argparse.ArgumentParser(description='Convert json from stdin to Kaldi input files (in output-folder).')
parser.add_argument('--output-folder', type=str, required=True,
                    help='The output folder')
parser.add_argument('--no-silence-markers', action="store_true", help='The input json file')
args = parser.parse_args()

#input_json_fname = args.input_json;
output_folder = args.output_folder;
silence_markers = not args.no_silence_markers;


#f_in = open(input_json_fname, "r");
f_in = sys.stdin;

json_transcripts = json.loads(f_in.read());
f_in.close();

speakers = {};
recordings = {};
utterances = {};

if not os.path.exists(output_folder):
	os.makedirs(output_folder);

f_segments = open(output_folder + "/segments", "w", encoding="utf-8");
f_transcripts = open(output_folder + "/text", "w", encoding="utf-8");
f_speakers = open(output_folder + "/spk2gender", "w", encoding="utf-8");
f_recordings = open(output_folder + "/wav.scp", "w", encoding="utf-8");
f_utt2spk = open(output_folder + "/utt2spk", "w", encoding="utf-8");
f_corpus = open(output_folder + "/corpus.txt", "w", encoding="utf-8");

for json_transcript in json_transcripts:
    transcript = json_transcript["transcript"];
    startMs = json_transcript["startMs"];
    stopMs = json_transcript["stopMs"];
    speakerId = json_transcript["speakerId"];
    audioFileName = json_transcript["audioFileName"].replace("\\", "/");

    if speakerId not in speakers:
        speakers[speakerId] = str(uuid.uuid4()); # create speaker id
        f_speakers.write(speakers[speakerId] + " " + "f\n"); # writing gender

    if audioFileName not in recordings:
        recordings[audioFileName] = str(uuid.uuid4()); # create recording id
        f_recordings.write(recordings[audioFileName] + " " + audioFileName + "\n");

    speaker_id = speakers[speakerId];
    recording_id = recordings[audioFileName];
    utterance_id = speakers[speakerId] + "-" + str(uuid.uuid4());

    if silence_markers:
      f_transcripts.write(utterance_id + " !SIL " + transcript + " !SIL\n");
    else:
      f_transcripts.write(utterance_id + " " + transcript + "\n");
    f_segments.write(utterance_id + " " + recording_id + " " + "%f %f\n" % (startMs / 1000.0, stopMs / 1000.0));
    #f_utt2spk.write(utterance_id + " " + speaker_id + "\n");
    f_utt2spk.write(utterance_id + " " + utterance_id + "\n"); # hack to match utterances to utterances
    f_corpus.write(transcript + "\n");


f_segments.close();
f_transcripts.close();
f_speakers.close();
f_recordings.close();
f_utt2spk.close();
f_corpus.close();
