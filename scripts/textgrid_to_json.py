import os
import sys
import argparse

parser = argparse.ArgumentParser(description='Search input-folder for .TextGrid files and convert to JSON on stdout')
parser.add_argument('--input-dir', type=str, required=True, help='The input folder')
args = parser.parse_args()

corpus_root = args.input_dir

DEFAULT = 0
START_READING = 1
START_INTERVAL = 2


def extract_textgrid_intervals(filename):
    path_file = os.path.join(os.getcwd(), root, filename)
    state = DEFAULT

    intervals = []
    current_interval = {}
    # _, name = os.path.split(filename)
    # basename, _ = os.path.splitext(name)
    # current_interval["wavfilename"] = os.path.join(".", basename + ".wav")

    # , encoding="ISO-8859-1" whwen we use this ISO, 'if word in line' fails!
    f = open(path_file, "r")

    for line in f:
        if "Speech" in line:
            state = START_READING

        if state == START_READING:
            if "intervals [" in line:
                state = START_INTERVAL
        elif state == START_INTERVAL:
            if "intervals [" in line:
                if current_interval["text"] != "":
                    intervals.append(current_interval)
                current_interval = {}

            elif "item [" in line:
                if current_interval["text"] != "":
                    intervals.append(current_interval)
                current_interval = {}
                state = DEFAULT

            elif "xmin" in line:
                current_interval["xmin"] = line.split()[2]
            elif "xmax" in line:
                current_interval["xmax"] = line.split()[2]
            elif "text" in line:
                text = line.split("=")[1].strip()
                if text != "":
                    if text[0] == "\"":
                        text = text[1:]

                    if text != "" and text[-1] == "\"":
                        text = text[:-1]

                # need to clean the text here, else it could create invalid json
                # let's start by stripping quotes
                current_interval["text"] = text.replace('"', '')
    f.close()
    return intervals


def sec2milli(seconds):
    return seconds * 1000


def write_json(filename, intervals):
    # here is where we ignore the filename and replace with stdout
    json_f = sys.stdout

    # Get paths to files
    inDir, name = os.path.split(filename)
    basename, ext = os.path.splitext(name)

    def print_interval(interval, final):
        print("{", file=json_f)
        print("\"transcript\": \"%s\"," % interval["text"], file=json_f)
        print("\"startMs\": %f," % sec2milli(float(interval["xmin"])), file=json_f)
        print("\"stopMs\": %f," % sec2milli(float(interval["xmax"])), file=json_f)
        print("\"speakerId\": \"\",", file=json_f)
        print("\"audioFileName\": \"%s\"" % os.path.join(".", basename + ".wav"), file=json_f)
        if final:
            print("}", file=json_f)
        else:
            print("},", file=json_f)

    print("[", file=json_f)
    for interval in intervals[:-1]:
        print_interval(interval, final=False)
    print_interval(intervals[-1], final=True)
    print("]", file=json_f)


intervals = []

for (root, dirs, files) in os.walk(corpus_root):
    for filename in files:
        if filename.endswith(".TextGrid"):
            intervals.extend(extract_textgrid_intervals(filename))

write_json(filename, intervals)
