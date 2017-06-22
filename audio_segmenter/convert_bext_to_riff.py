
import os;
from subprocess import call;

def process(filename):

    name = filename.rsplit(".", 1)[0];

    input_name = name + ".wav";
    riff_name = name + "_riff.wav";
    mono_name = name + "_mono.wav";

    print input_name;


    call("sox '" + input_name + "' '" + riff_name + "'", shell=True);
    call("sox '" + riff_name + "' '" + mono_name + "' remix 1", shell=True);
    call("mv '" + mono_name + "' '" + input_name + "'", shell=True);

    call("rm '" + "' '".join([riff_name]) + "'", shell=True);


for (root, dirs, files) in os.walk("."):
    for filename in files:
        if filename.endswith(".wav"):
            process(root + "/" + filename);
