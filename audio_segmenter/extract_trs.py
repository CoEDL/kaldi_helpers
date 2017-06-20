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

import json
import platform

#g_sampleRate = 8000
#g_sampleRateHq = 48000

parser = argparse.ArgumentParser(description='.', formatter_class=argparse.RawDescriptionHelpFormatter)

#parser.add_argument('integers', metavar='N', type=int, nargs='+', help='an integer for the accumulator')
#parser.add_argument('-t', '--tmp', dest='tmpDir', help='Temporary directory, default is <inputDir>/tmp', default = '')
parser.add_argument('-d', '--indir', dest='inputDir', help='Input directory, default=\'.\'', default = '.')
#parser.add_argument('-f', '--ffmpegpath', dest='ffmpegPath', help='Path to ffmpeg executable (including exe), default=\'ffmpeg\'', default = '')
parser.add_argument('-v', '--verbose', dest='verbose', help='Turn on piping all ffmpeg output to the std streams (otherwise it is hidden), defaults to False', action="store_true")

args = parser.parse_args()

g_baseDir = args.inputDir;
#g_tmpDir = os.path.join(g_baseDir, "tmp");

#if args.tmpDir != '':
#    g_tmpDir = args.tmpDir

#g_outDir = os.path.join(g_baseDir, "output");


#g_ffmpegExe = "c:\\tools\\ffmpeg\\bin\\ffmpeg"
#g_ffmpegExe = spawn.find_executable(os.path.join(args.ffmpegPath, "ffmpeg"))
#g_ffprobeExe = spawn.find_executable(os.path.join(args.ffmpegPath, "ffprobe"))

#if g_ffmpegExe == None or g_ffprobeExe == None:
#    print("Could not find ffmpeg! Please ensure full path is given using '-f' or that the bin directory is on the system path!");
#    print("  ffmpeg path: %s"%g_ffmpegExe)
#    print("  ffprobe path: %s"%g_ffprobeExe)
#    sys.exit(1)

g_verboseOutput = args.verbose

if g_verboseOutput:
    print(g_baseDir)
    #print(g_tmpDir)
    #print(g_ffmpegExe)


# Create temp directory if not there
#if not os.path.exists(g_tmpDir):
#    os.makedirs(g_tmpDir)

#if not os.path.exists(g_outDir):
#    os.makedirs(g_outDir)


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
        # Super-annoying mumbojumbo to work around utf8 file name and the windows console which under the debugger claims to be utf8 but then fails regardless!
        if platform.system() == 'Windows':
            sys.stdout.write(text.encode('cp850', errors='backslashreplace').decode(sys.stdout.encoding))
        else:
            sys.stdout.write(text)
        sys.stdout.flush()


allFilesInDir = set(glob.glob(os.path.join(g_baseDir, "**"), recursive = True))

transcriptNames = findFilesByExt(allFilesInDir, set(["*.trs"]));
#print(transcriptNames)
#def outputAudioSegment(fileName, startTime, endTime, transStr, outBaseName):
    #print(fileName, startTime, endTime, transStr)
    #ffmpeg -ss 0 -i file.mp3 -t 30 file.wav
#    execProc([g_ffmpegExe, "-ss", "%f"%startTime, "-i", fileName, "-t", "%f"%(endTime-startTime), outBaseName + ".wav"], "time=\s*(?P<progress>\S+)\s")
#    with open(outBaseName + ".txt", 'w') as outTranscriptFile:
#        outTranscriptFile.write(transStr);


def processFile(fileName):
    condLog(g_verboseOutput, "Processing transcript '%s'\n"%fileName)
    #global g_outDir

    utterances = []
    try:
        tree = ET.parse(fileName)
        root = tree.getroot()
        waveName = root.attrib['audio_filename'] + ".wav"
        turnNodes = tree.findall(".//Turn")

        for turnNode in turnNodes:
            utterances = utterances + processTurn(fileName, turnNode, waveName, tree)
    except ET.ParseError as err:
        condLog(True, "XML parser failed to parse '%s'!\n"%fileName)
    return utterances

def processTurn(fileName, turnNode, waveName, tree):

    turnStart = float(turnNode.attrib['startTime'])
    turnEnd = float(turnNode.attrib['endTime'])
    speakerId = turnNode.get('speaker', '')

    speakerNameNode = tree.find(".//Speaker[@id='%s']"%speakerId)
    speakerName = ""
    if speakerNameNode != None:
        speakerName = speakerNameNode.attrib['name']

    items = [(ch.attrib['time'], ch.tail.strip()) for ch in turnNode.findall("./Sync")]

    #create subDir in output
    baseDir,name = os.path.split(fileName)
    baseName, _ = os.path.splitext(name)
    waveFileName = os.path.join(baseDir, waveName)
    #outDir = os.path.join(g_outDir, baseName);
    #if not os.path.exists(outDir):
    #    os.makedirs(outDir)

    result = []

    #for timeStr,transStr in items:
    for i in range(0, len(items)):
        timeStr,transStr = items[i]
        startTime = float(timeStr)
        if i < len(items) - 1:
            timeStr2,_ = items[i+1]
            endTime = float(timeStr2)
        else:
            endTime = turnEnd
        #outBaseName = os.path.join(outDir, "%08d"%i)
        #outputAudioSegment(waveFileName, startTime, endTime, transStr, outBaseName)
        result.append({"speakerId" : speakerName, "audioFileName" : waveFileName, "transcript" : transStr, "startMs" : startTime * 1000.0, "stopMs" : endTime * 1000.0})
        startTime = endTime
    #print("done")
    return result


# iterate through all .trs files and process them, creates audio clip files and returns the set {fileName, transcriptString, speakerID}
utterances = []
for fn in transcriptNames:
    utterances = utterances + processFile(fn)

#print(utterances)
#with open("jeff.json", "w") as f:
#    f.write(json.dumps(utterances))

resultBaseName,name = os.path.split(g_baseDir)

if name == '.':
    outFileName = "utterances.json"
else:
    outFileName = name + ".json"

with open(outFileName, 'w') as outfile:
    json.dump(utterances, outfile, indent=2)