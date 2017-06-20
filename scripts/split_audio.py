import xml.etree.ElementTree as ET
#import timeit
import glob
import sys
import os
import re
import itertools
import difflib
import subprocess
import argparse
#import json
from distutils import spawn

#g_sampleRate = 8000
#g_sampleRateHq = 48000

parser = argparse.ArgumentParser(description='.', formatter_class=argparse.RawDescriptionHelpFormatter)

#parser.add_argument('integers', metavar='N', type=int, nargs='+', help='an integer for the accumulator')
#parser.add_argument('-t', '--tmp', dest='tmpDir', help='Temporary directory, default is <inputDir>/tmp', default = '')
parser.add_argument('-d', '--indir', dest='inputDir', help='Input directory, default=\'.\'', default = '.')
parser.add_argument('-f', '--ffmpegpath', dest='ffmpegPath', help='Path to ffmpeg executable (including exe), default=\'ffmpeg\'', default = '')
parser.add_argument('-v', '--verbose', dest='verbose', help='Turn on piping all ffmpeg output to the std streams (otherwise it is hidden), defaults to False', action="store_true")

args = parser.parse_args()

g_baseDir = args.inputDir;
#g_tmpDir = os.path.join(g_baseDir, "tmp");

#if args.tmpDir != '':
#    g_tmpDir = args.tmpDir

g_outDir = os.path.join(g_baseDir, "output");


#g_ffmpegExe = "c:\\tools\\ffmpeg\\bin\\ffmpeg"
g_ffmpegExe = spawn.find_executable(os.path.join(args.ffmpegPath, "ffmpeg"))
g_ffprobeExe = spawn.find_executable(os.path.join(args.ffmpegPath, "ffprobe"))

if g_ffmpegExe == None or g_ffprobeExe == None:
    print("Could not find ffmpeg! Please ensure full path is given using '-f' or that the bin directory is on the system path!");
    print("  ffmpeg path: %s"%g_ffmpegExe)
    print("  ffprobe path: %s"%g_ffprobeExe)
    sys.exit(1)

g_verboseOutput = args.verbose

if g_verboseOutput:
    print(g_baseDir)
    #print(g_tmpDir)
    print(g_ffmpegExe)


# Create temp directory if not there
#if not os.path.exists(g_tmpDir):
#    os.makedirs(g_tmpDir)

if not os.path.exists(g_outDir):
    os.makedirs(g_outDir)


def execProc(procArgs, progressPattern):
    global g_verboseOutput

    if g_verboseOutput:
        subprocess.call(procArgs)
        return

    procArgs.append("-y")
    process = subprocess.Popen(procArgs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    count=0    
    tmpStr = ""
    while process.poll() == None:
        buff = process.stdout.read(1)

        tmpStr += buff.decode()

        if g_verboseOutput:
            sys.stdout.write(buff.decode())#, end = '', flush = True)
            sys.stdout.flush()

        tmpStr.replace('\r', '\n')

        #if tmpStr.find('frame') > -1:
        #    tmpStr = tmpStr[tmpStr.find('frame'):]

        result = re.search(progressPattern, tmpStr)
        if result != None and 'progress' in result.groupdict():
            sys.stdout.write("\rframe=%s"%result.groupdict()['progress'])#, end = '', flush = True)
            sys.stdout.flush()
            tmpStr = ""

    process.wait()


def findFirstFileByExt(setOfAllFiles, exts):
    for f in setOfAllFiles:
        name, ext = os.path.splitext(f)
        if ("*" + ext.lower()) in exts:
            return f
    return ""

def findFilesByExt(setOfAllFiles, exts):
    res = []
    for f in setOfAllFiles:
        name, ext = os.path.splitext(f)
        if ("*" + ext.lower()) in exts:
            res.append(f)
    return res
    
def condLog(cond, text):
    if cond:
        sys.stdout.write(text)
        sys.stdout.flush()


allFilesInDir = set(glob.glob(os.path.join(g_baseDir, "*.*")))

transcriptNames = findFilesByExt(allFilesInDir, "*.trs");

def outputAudioSegment(fileName, startTime, endTime, transStr, outBaseName):
    #print(fileName, startTime, endTime, transStr)
    #ffmpeg -ss 0 -i file.mp3 -t 30 file.wav
    execProc([g_ffmpegExe, "-ss", "%f"%startTime, "-i", fileName, "-t", "%f"%(endTime-startTime), outBaseName + ".wav"], "time=\s*(?P<progress>\S+)\s")
    with open(outBaseName + ".txt", 'w') as outTranscriptFile:
        outTranscriptFile.write(transStr);


def processFile(fileName):
    print("Processing transcript '%s'"%fileName)
    global g_outDir
    tree = ET.parse(fileName)
    root = tree.getroot()
    waveName = root.attrib['audio_filename'] + ".wav"
    turnNode = tree.find(".//Turn")
    turnStart = float(turnNode.attrib['startTime'])
    turnEnd = float(turnNode.attrib['endTime'])

    items = [(ch.attrib['time'], ch.tail.strip()) for ch in turnNode]

    #create subDir in output
    baseDir,name = os.path.split(fileName)
    baseName, _ = os.path.splitext(name)
    waveFileName = os.path.join(baseDir, waveName)
    outDir = os.path.join(g_outDir, baseName);
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    #for timeStr,transStr in items:
    for i in range(0, len(items)):
        timeStr,transStr = items[i]
        startTime = float(timeStr)
        if i < len(items) - 1:
            timeStr2,_ = items[i+1]
            endTime = float(timeStr2)
        else:
            endTime = turnEnd
        outBaseName = os.path.join(outDir, "%08d"%i)
        outputAudioSegment(waveFileName, startTime, endTime, transStr, outBaseName)
        startTime = endTime
    print("done")
for fn in transcriptNames:
    processFile(fn)