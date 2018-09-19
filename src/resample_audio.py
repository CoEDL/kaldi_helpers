#!/usr/bin/python3

"""
Convert audio to 16 bit 16k mono WAV

@author Ola Olsson 2018
"""

import argparse
import glob
import os
import subprocess
import threading
from multiprocessing.dummy import Pool
from shutil import move
from src.utilities.file_utilities import find_files_by_extension


def process_item(xx, tmpFolders, g_soxPath):
    print("processing")
    inInd, ia = xx
    global g_tmpDir
    global g_processLock
    global g_outputStep

    with g_processLock:
        print("[%d, %d]%s" % (g_outputStep, inInd, ia))
        g_outputStep += 1

    inputName = os.path.normpath(ia)
    # 1. convert using sox

    inDir, name = os.path.split(ia)
    print(inDir)
    baseName, ext = os.path.splitext(name)
    outDir = os.path.join(inDir, g_tmpDir)
    print(outDir)
    tmpFolders.add(outDir)

    # avoid race condition
    with g_processLock:
        if not os.path.exists(outDir):
            os.makedirs(outDir)

    tmpAudioName = joinNorm(outDir, "%s.%s" % (baseName, "wav"))

    if not os.path.exists(tmpAudioName):
        cmdLn = [g_soxPath, inputName, "-b", "16", "-c", "1", "-r", "44.1k", "-t", "wav", tmpAudioName]
        subprocess.call(cmdLn)
    return tmpAudioName


def joinNorm(p1, p2):
    tmp = os.path.join(os.path.normpath(p1), os.path.normpath(p2))
    return os.path.normpath(tmp)


def main():
    parser = argparse.ArgumentParser(
        description="This script will silence a wave file based on annotations in an Elan tier ")
    parser.add_argument('-c', '--corpus', help='Directory of audio and eaf files', type=str, default='../input/data')
    parser.add_argument('-o', '--overwrite', help='Write over existing files', type=str, default='yes')
    args = parser.parse_args()

    overwrite = args.overwrite
    g_baseDir = args.corpus
    g_audioExts = ["*.wav"]
    g_soxPath = "/usr/bin/sox"
    g_tmpDir = "tmp"

    allFilesInDir = set(glob.glob(os.path.join(g_baseDir, "**"), recursive=True))
    inputAudio = find_files_by_extension(allFilesInDir, set(g_audioExts))
    g_processLock = threading.Lock()
    g_outputStep = 0

    outputs = []
    tmpFolders = set([])

    # Single thread
    # outputs.append(processItem(ia))

    # Multithread
    with Pool() as p:
        outputs = p.map(process_item, enumerate(inputAudio))

        if overwrite == 'yes':
            # Replace original files
            for f in outputs:
                fname = os.path.basename(f)
                parent = os.path.dirname(os.path.dirname(f))
                move(f, os.path.join(parent, fname))
            # Clean up tmp folders
            for d in tmpFolders:
                os.rmdir(d)


