from __future__ import print_function
import os;
from subprocess import call;


DEFAULT = 0;
START_READING = 1;
START_INTERVAL = 2;


def extract_textgrid_intervals(filename): #, scp_out, json_out):
    global id;

    state = DEFAULT;

    intervals = [];
    current_interval = {};
    current_interval["audioFileName"] = filename

    f = open(filename, "r");

    for line in f:
        #print line;
        if "Abui" in line:
            state = START_READING;

        if state == START_READING:
            if "intervals [" in line:
                state = START_INTERVAL;
        elif state == START_INTERVAL:
            if "intervals [" in line:
                if current_interval["text"] != "":
                    intervals.append(current_interval);
                current_interval = {};
                current_interval["audioFileName"] = filename

            elif "item [" in line:
                if current_interval["text"] != "":
                    intervals.append(current_interval);
                current_interval = {};
                current_interval["audioFileName"] = filename
                state = DEFAULT;

            elif "xmin" in line:
                current_interval["xmin"] = line.split()[2];
            elif "xmax" in line:
                current_interval["xmax"] = line.split()[2];
            elif "text" in line:
                text = line.split("=")[1].strip();

                #if text[0] != "\"" or text[-1] != "\"":
                #   print text;
                #    assert(text[0] == "\"" and text[-1] == "\"");
                if text != "":
                    print(text)
                    if text[0] == "\"":
                        text = text[1:];

                    if text != "" and text[-1] == "\"":
                        text = text[:-1];

                current_interval["text"] = text;



    f.close();

    return intervals;

def sec2milli(seconds):
    return seconds*1000

def write_json(json_fn, intervals):
    with open(json_fn, "w") as json_f:

        def print_interval(interval):
            print("{", file=json_f)
            print("\"transcript\": \"%s\"," % interval["text"], file=json_f)
            print("\"startMs\": %f," % sec2milli(float(interval["xmin"])), file=json_f)
            print("\"stopMs\": %f," % sec2milli(float(interval["xmax"])), file=json_f)
            print("\"speakerId\": \"\",", file=json_f)
            audiofn = interval["audioFileName"].rsplit(".", 1)[0] + ".wav"
            print("\"audioFileName\": \"%s\"," % audiofn, file=json_f)
            print("},", file=json_f)


        print("[", file=json_f)
        for interval in intervals:
            print_interval(interval)
        print("]", file=json_f)

#    wav_fn = filename.rsplit(".", 1)[0];

#    try:
#        os.makedirs("wav_output/" + os.path.dirname(wav_fn));
#    except:
#        pass;


#    f_out = open("wav_output/" + wav_fn + ".txt", "w");
#    for i, interval in enumerate(intervals):
#        #call("sox '%s.wav' 'wav_output/%s_%04i.wav' trim %s =%s" % (wav_fn, wav_fn, i, interval["xmin"], interval["xmax"]), shell=True);
#        f_out.write("%s %s %s\n" % (interval["xmin"], interval["xmax"], interval["text"]));
#        scp_out.write("_%010i '%s_%04i.wav'\n" % (id, wav_fn, i));
#        id += 1;
#    f_out.close();


#sox in.mp3 out.mp3 trim 2 0.195


#scp_out = open("wav_output/wav.scp", "w");
id = 0;

intervals = []
for (root, dirs, files) in os.walk("."):
    for filename in files:
        if filename.endswith(".TextGrid"):
            print(root, filename);
            intervals.extend(extract_textgrid_intervals(root + "/" + filename));

json_fn = "wav_output/textgrid.json"
write_json(json_fn, intervals)
#scp_out.close();
