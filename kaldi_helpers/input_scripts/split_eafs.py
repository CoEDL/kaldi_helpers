#!/usr/bin/python3

"""
Copyright Ben Foley ben@cbmm.io 30 Jan 2018

Split Elan .eaf and .wav audio file by the start and end times of annotations on a particular tier
Don't worry about 'Parsing unknown version of ELAN spec... ' warnings,
pympi is looking for v 2.7 or 2.8 of elan schema
"""


import argparse
import glob
import json
import os
import sys
from pydub import AudioSegment
from pympi.Elan import Eaf


def split_audio_by_start_end(input_audio, start, end, fname, ext, output_audio_dir):
    output = input_audio[start:end]
    output.export(os.path.join(output_audio_dir, fname + ext), format=ext[1:])


def write_text(annotation, fname, ext, output_text_dir):
    f = open(os.path.join(output_text_dir, fname + ext), 'w')
    f.write(annotation)
    f.close()


def write_json(annotations_data, output_json):
    with open(output_json, 'w') as outfile:
        json.dump(annotations_data, outfile, indent=4, separators=(',', ': '), sort_keys=False)


def read_eaf(ie, tier, silence_tier, silence_marker, json_data, output_text_dir, output_audio_dir):

    input_eaf = Eaf(ie)

    # Check if the tiers we have been given exist
    tier_names = input_eaf.get_tier_names()
    if tier not in tier_names:
        print('missing tier: ' + tier, file=sys.stderr)
        return False
    if silence_tier not in tier_names:
        print('missing silence tier: ' + silence_tier, file=sys.stderr)

    # get the input_scripts audio file
    inDir, name = os.path.split(ie)
    basename, ext = os.path.splitext(name)
    ia = os.path.join(inDir, basename + ".wav")
    input_audio = AudioSegment.from_wav(ia)

    # We can pass in an arg for a ref tier that has silence labels
    check_silence_ref_tier = False
    if silence_tier in tier_names:
        silence_tier_info = input_eaf.get_parameters_for_tier(silence_tier)
        if silence_tier_info.get("PARENT_REF") == tier:
            check_silence_ref_tier = True

    # Get annotation values, start and end times, and speaker id
    annotations = sorted(input_eaf.get_annotation_data_for_tier(tier))
    params = input_eaf.get_parameters_for_tier(tier)
    if 'PARTICIPANT' in params:
        speaker_id = params['PARTICIPANT']

    i = 0
    for ann in annotations:
        skip = False
        start = ann[0]
        end = ann[1]
        # output_scripts new values, not the original clip start end times
        clip_start = 0
        clip_end = ann[1] - ann[0]
        annotation = ann[2]

        # Check for annotations labelled with a particular symbol on the main tier
        if annotation == silence_marker:
            skip = True

        # Check for existence of an annotation in ref tier to silence
        # Annotation value doesn't matter
        if check_silence_ref_tier and len(input_eaf.get_ref_annotation_at_time(silence_tier, start)):
            skip = True

        if skip is True:
            # print('skipping annotation: ' + annotation, start, end)
            print("skipping" + str(i))
        else:
            print("processing" + str(i))
            # print('processing annotation: ' + annotation, start, end)
            # build the output_scripts audio/text filename
            fname = basename + "_" + str(i)
            obj = {
                'audioFileName': os.path.join(".", fname + ".wav"),
                'transcript': annotation,
                'startMs': clip_start,
                'stopMs': clip_end
            }
            if 'PARTICIPANT' in params:
                obj["speakerId"] = speaker_id
            json_data.append(obj)
            split_audio_by_start_end(input_audio, start, end, fname, ".wav", output_audio_dir)
            write_text(annotation, fname, ".txt", output_text_dir)
            i += 1


def findFilesByExt(setOfAllFiles, exts):
    res = []
    for f in setOfAllFiles:
        name, ext = os.path.splitext(f)
        if ("*" + ext.lower()) in exts:
            res.append(f)
    return res


def main():
    parser = argparse.ArgumentParser(
        description="Slices a directory of Elan .eaf files and matching .wav files into separate "
                    "audio and text files by the start and end times of each annotation in a particular tier. "
                    "Annotations with a particular value can be skipped. Annotations on a ref tier can be used"
                    " to skip annotations in the target tier.")
    parser.add_argument('-i', '--input_dir',
                        help='Directory of dirty audio and eaf files',
                        type=str,
                        default='../input_scripts/data-dirty')
    parser.add_argument('-t', '--tier',
                        help='Target language tier name',
                        type=str,
                        default='Phrase')
    parser.add_argument('-m', '--silence_marker',
                        help='Skip annotation with this value on the target language tier',
                        type=str,
                        default='*PUB')
    parser.add_argument('-s', '--silence_tier',
                        help='Silence audio when annotations are found on this ref tier',
                        type=str,
                        default='Silence')
    parser.add_argument('-a', '--output_audio_dir',
                        help='Dir to save the audio files',
                        type=str,
                        default='../input_scripts/data')
    parser.add_argument('-o', '--output_text_dir',
                        help='Directory to save sliced text files',
                        type=str,
                        default='../input_scripts/output_scripts/tmp/label')
    parser.add_argument('-j', '--output_json',
                        help='File name to output_scripts json',
                        type=str,
                        default='../input_scripts/output_scripts/tmp/dirty.json')
    args = parser.parse_args()
    try:
        input_dir = args.input_dir
        tier = args.tier
        silence_marker = args.silence_marker
        silence_tier = args.silence_tier
        output_audio_dir = args.output_audio_dir
        output_text_dir = args.output_text_dir
        output_json = args.output_json
    except Exception:
        parser.print_help()
        sys.exit(0)

    if not os.path.exists(output_audio_dir):
        os.makedirs(output_audio_dir)
    if not os.path.exists(output_text_dir):
        os.makedirs(output_text_dir)

    g_exts = ["*.eaf"]
    allFilesInDir = set(glob.glob(os.path.join(input_dir, "**"), recursive=True))
    input_eafs = findFilesByExt(allFilesInDir, set(g_exts))
    json_data = []

    for ie in input_eafs:
        read_eaf(ie, tier, silence_tier, silence_marker, json_data, output_text_dir, output_audio_dir)

    # output_scripts the json data for the next step in kaldi pipeline
    write_json(json_data, output_json)

if __name__ == "__main__":
    main()
