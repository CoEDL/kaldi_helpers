"""
extracts the xml to text
'.//TIER[@LINGUISTIC_TYPE_REF="text"]/ANNOTATION/REF_ANNOTATION/ANNOTATION_VALUE
"""
import xml.etree.ElementTree as ET
import os
import re


input_dir = '/home/paul/google_meetup/text_processing/Komnzo'
output_file = '/home/paul/google_meetup/text_processing/Komnzo_out/output.txt'
nonallowed = '"#.,?()1234567890*'     # chars not allowed
linguistic_ref = 'text'
temp = []

def strip_allowed(text):
    """
    remove non allowed chars
    :param text:
    :return:
    """
    for index in range(0, len(nonallowed)):
        text = text.replace(nonallowed[index], '')
    return text.lower()

def read_elan_tier(filename):
    _raw_data = open(filename, 'r').read()
    _raw_data = re.sub('\s+', ' ', _raw_data)
    _tree = ET.fromstring(_raw_data)
    _nodes = _tree.findall('.//TIER[@LINGUISTIC_TYPE_REF="' + linguistic_ref
                           + '"]/ANNOTATION/ALIGNABLE_ANNOTATION/ANNOTATION_VALUE')
    _ret = []
    for _node in _nodes:
        _node_text = _node.text
        if _node_text is not None:
            _node_text = strip_allowed(_node_text)
        _ret.append(_node_text)
    return _ret


def find_unique_words(wordlist):
    """
    appends the current word list to the temp (output) list
    :param wordlist:
    :return:
    """
    for word in wordlist:
        if word is not None:
            wordsplit = word.split(' ')
            for w in wordsplit:
                if w not in temp and len(w)>0:
                    temp.append(w)


def process_file(inputfile):
    print('File > ' + inputfile)
    _chunks = read_elan_tier(inputfile)
    find_unique_words(_chunks)


# load non allowed files
_files = os.listdir(input_dir)
for _file in _files:
    if _file.endswith('.eaf'):
        process_file(input_dir + '/' + _file)

# write temp (output)
temp = sorted(temp)
_out = open(output_file, 'w')
for word in temp:
    _out.write(word + '\n')
_out.close()

