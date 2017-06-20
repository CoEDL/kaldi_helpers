
import os;
from subprocess import call;


DEFAULT = 0;
START_READING = 1;
START_INTERVAL = 2;


def process_textgrid(filename, scp_out):
    global id;

    state = DEFAULT;

    intervals = [];
    current_interval = {};


    f = open(filename, "r");

    for line in f:
        #print line;
        if "Abui" in line:
            state = START_READING;

        if state == START_READING:
            if "intervals [" in line:
                state = START_INTERVAL;
        elif state == START_INTERVAL:
            print "START_INTERVAL"
            if "intervals [" in line:
                if current_interval["text"] != "":
                    intervals.append(current_interval);
                current_interval = {};

            elif "item [" in line:
                if current_interval["text"] != "":
                    intervals.append(current_interval);
                current_interval = {};
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
                    print text;
                    if text[0] == "\"":
                        text = text[1:];

                    if text != "" and text[-1] == "\"":
                        text = text[:-1];

                current_interval["text"] = text;



    f.close();

    print intervals;

    wav_fn = filename.rsplit(".", 1)[0];

    try:
        os.makedirs("wav_output/" + os.path.dirname(wav_fn));
    except:
        pass;


    f_out = open("wav_output/" + wav_fn + ".txt", "w");
    for i, interval in enumerate(intervals):
        call("sox '%s.wav' 'wav_output/%s_%04i.wav' trim %s =%s" % (wav_fn, wav_fn, i, interval["xmin"], interval["xmax"]), shell=True);
        f_out.write("%s %s %s\n" % (interval["xmin"], interval["xmax"], interval["text"]));
        scp_out.write("_%010i '%s_%04i.wav'\n" % (id, wav_fn, i));
        id += 1;
    f_out.close();


#sox in.mp3 out.mp3 trim 2 0.195

scp_out = open("wav_output/wav.scp", "w");
id = 0;
for (root, dirs, files) in os.walk("."):
    for filename in files:
        if filename.endswith(".TextGrid"):
            print root, filename;
            process_textgrid(root + "/" + filename, scp_out);

scp_out.close();
