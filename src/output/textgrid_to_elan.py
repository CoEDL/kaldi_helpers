#!/usr/bin/python

"""
# Copyright 2018 The University of Queensland (Author: Nicholas Lambourne)
# LICENCE: MIT
"""

from argparse import ArgumentParser
from pathlib import Path
from pympi import Praat


def main() -> None:
    parser: ArgumentParser = ArgumentParser(description="Converts Praat TextGrid format to ELAN eaf Format.")
    parser.add_argument("--tg", type=str, help="The input TextGrid format file", required=True)
    parser.add_argument("--outfile", type=str, help="The file path for the ELAN file output",
                        default="./inference.eaf")
    arguments = parser.parse_args()

    textgrid_file = arguments.tg
    output_file = Path(arguments.outdir)

    if not output_file.parent:
        Path.mkdir(output_file.parent, parents=True)

    textgrid = Praat.TextGrid(file_path=textgrid_file)

    elan = textgrid.to_eaf()

    elan.to_file(output_file)


if __name__ == '__main__':
    main()
