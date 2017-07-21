import xml.etree.ElementTree as ET
import glob
import sys
import os
import argparse
import json
import platform
import uuid
from distutils import spawn
import subprocess
import re

parser = argparse.ArgumentParser(description='.', formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument('file', nargs='?', help='Input&output json file')
parser.add_argument('-v', '--verbose', dest='verbose', help='More logging to console.', action="store_true")
parser.add_argument('-f', '--ffmpegpath', dest='ffmpegPath', help='Path to ffmpeg executable (including exe), default=\'ffmpeg\'', default = '')

args = parser.parse_args()

g_verboseOutput = args.verbose
g_inFile = args.file;

g_ffmpegExe = spawn.find_executable(os.path.join(args.ffmpegPath, "ffmpeg"))


if g_ffmpegExe == None:
    print("Could not find ffmpeg! Please ensure full path is given using '-f' or that the bin directory is on the system path!");
    print("  ffmpeg path: %s"%g_ffmpegExe)
    sys.exit(1)

if g_verboseOutput:
    print(g_inFile)
    print(g_ffmpegExe)


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

        tmpStr += buff.decode(errors="ignore")

        if g_verboseOutput:
            sys.stdout.write(buff.decode(errors="ignore"))#, end = '', flush = True)
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

#_,name = os.path.split(g_inFile)
inBaseName, inExt = os.path.splitext(g_inFile)

g_outDir = os.path.join(".", inBaseName.replace("\\", "-").replace(".", "-") + "-split-audio")
if not os.path.exists(g_outDir):
    os.makedirs(g_outDir)

with open(g_inFile, 'r') as inFile:
    utterances = json.load(inFile)

#print(utterances)

outputCounter = 0

def processUtterance(ut):
    global outputCounter
    global g_outDir
    audioName = ut['audioFileName']
    startTime = float(ut['startMs']) / 1000.0
    endTime = float(ut['stopMs']) / 1000.0
    _,name = os.path.split(audioName)
    baseName, ext = os.path.splitext(name)
    
    outName = os.path.join(g_outDir, "%s_%08d.%s"%(baseName,outputCounter,ext))
    execProc([g_ffmpegExe, "-ss", "%f"%startTime, "-i", audioName, "-t", "%f"%(endTime-startTime), outName], "time=\s*(?P<progress>\S+)\s")
    outputCounter = outputCounter + 1
    
    ut['audioFileName'] = outName
    ut['startMs']  = 0.0
    ut['stopMs'] * (endTime-startTime) * 1000.0
        
    return ut

utterances = [processUtterance(ut) for ut in utterances]

with open(inBaseName + "-split-audio" + inExt, 'w') as outfile:
    json.dump(utterances, outfile, indent=2)    