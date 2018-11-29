#!/usr/bin/python3
#
# this is a file for automatically build the word->sound dictionary
# input: text file, config file
# output: mapping between unique words and their sound, ordered by their appearance

import argparse
import sys


def generate_dictionary(input_file_name: str,
                        output_file_name: str,
                        config_file_name: str):
    # read the input_scripts file
    input_file = open(input_file_name, "r", encoding='utf-8')
    input_tokens = []
    for line in input_file.readlines():
        token = line.strip()

        if len(token) > 0:
            input_tokens.append(token)

    input_file.close()

    # read the config file
    config_file = open(config_file_name, "r", encoding='utf-8')
    sound_mappings = []

    for line in config_file.readlines():
        if line[0] == '#':
            continue

        mapping = list(filter(None, line.strip().split(' ', 1)))

        if len(mapping) > 1:
            sound_mappings.append((mapping[0], mapping[1]))

    config_file.close()

    # sort the sound mappings by length of sound mapping
    sound_mappings.sort(key=lambda x: len(x[0]), reverse=True)

    oov_characters = set([])

    output_file = open(output_file_name, "w", encoding='utf-8')
    output_file.write('!SIL sil\n')
    output_file.write('<UNK> spn\n')
    for token in input_tokens:
        current_index = 0
        res = [token]
        token_lower = token.lower()

        while current_index < len(token_lower):
            found = False
            for maps in sound_mappings:
                if token_lower.find(maps[0], current_index) == current_index:
                    found = True
                    res.append(maps[1])
                    current_index += len(maps[0])
                    break

            if not found:
                # unknown sound
                res.append('(' + token_lower[current_index] + ')')
                oov_characters.add(token_lower[current_index])
                current_index += 1

        output_file.write(' '.join(res) + '\n')

    output_file.close()

    for character in oov_characters:
        print("Unexpected character: %s" % character, file=sys.stderr)

    print("Done", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", required=True)
    parser.add_argument("--outfile", help="name of the output_scripts file", required=True)
    parser.add_argument("--config", help="configuration file with one letter -> sound mapping in each line")
    arguments = parser.parse_args()

    generate_dictionary(input_file_name=arguments.infile,
                        output_file_name=arguments.outfile,
                        config_file_name=arguments.config)


if __name__ == "__main__":
    main()
