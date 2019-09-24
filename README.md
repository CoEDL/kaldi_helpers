```
This repository is now deprecated in favour of [Elpis](https://github.com/CoEDL/elpis).
```


# CoEDL Kaldi Helpers <img src="docs/img/kh.png" align="right"/>

A set of scripts to use in preparing a corpus for speech-to-text processing with the [Kaldi](http://kaldi-asr.org/) 
Automatic Speech Recognition toolkit.

## Requirements

This pipeline relies on Python 3.6 and several open-source Python packages (listed [here](./requirements.txt)).
It also assumes you have Kaldi, [sox](http://sox.sourceforge.net/) and [task](https://taskfile.org/) installed.

## Tasks

This library uses the [task](https://taskfile.org) tool to run the more complex processes automatically. Once 
you've set up Kaldi Helpers, you can run the various pipeline tasks we've developed. Read the Taskfile for more information about the available tasks.
