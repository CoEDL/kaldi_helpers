# Recipes

## The ideal base ingredients
  
  Speech is transcribed by utterances, less than 10 seconds duration (words and phrases work well)

  Separate transcription file and audio file per utterance, or utterances are annotated in a single Elan tier

  Transcript and audio files have matching filenames
  
  Transcription text is lowercase, no punctuation, lexical forms only (no speaker or language codes or tags), target language only (no second language)

  If your data isn't quite in this format, one of these recipes may suit. The 'project setup' is common to all.


## Project Setup

All of the pipeline tasks require the data and config files that you provide to be situated in a particular place on your machine that the scripts can access.

Requirements: 
- a computer with Docker installed 
- command line software, eg Terminal on OSX
- some transcribed data

Create a working directory on your machine, e.g., `~/asr`
Inside asr, make an input folder `~/asr/input`
Inside this directory, make three folders: config, data and output `~/asr/input/config, ~/asr/input/data, ~/asr/input/output`
In the config folder, put your `letter_to_sound.txt`, `optional_silence.txt` and `silence_phones.txt` files.
Move your data into the input/data directory `~/asr/input/data/file1.eaf, ~/asr/input/data/file1.wav etc`

Follow the steps in the Docker guide to get a kaldi container...
https://github.com/CoEDL/kaldi-helpers/blob/master/guides/kaldi-docker-setup.md

Open Terminal (mac) or other command line program and type these commands (don't type the $)

    $ docker pull coedl/kaldi-helpers:0.2
    $ docker run -it --rm -v ~/asr/input/:/kaldi-helpers/input coedl/kaldi-helpers:0.2 /bin/bash

Now you're ready to run different recipes, depending on the shape and condition of your data. 



## Squeaky Clean Paleo Cupcakes

This recipe is for a data set with cleaned ELAN files. The .eaf files have only a single annotation in each (though there are likely to be multiple words in each utterance). All the audio has been converted earlier to suit the pipeline format.

Ingredients: 
- multiple ELAN files with a single annotation per file
- 16bit 44.1k mono audio files, with filenames matching corresponding ELAN files
- transcriptions were done by someone who was very obsessive about excluding non-target language, so there's no non-target language, or non-lexical entries

Method:
Follow the project setup steps to create the working project space and get Docker running.

At the Docker container's command prompt, type `task _run-elan-default` to start the tasks which convert your data into the formats that Kaldi expects and build the project (like the $, /kaldi-helpers# should already be there, don't type that):

    /kaldi-helpers# task _run-elan-default

If that runs OK, you'll see a message 'Build task completed without errors'. Ready to proceed to training. To train, type:

    /kaldi-helpers# task _train-test-default

Once that has finished, you should see a list of `%WER` and `%SER` values. These are your Word Error Rates and Sentence Error Rates. 

Done!


# The Dirty Martini

This recipe uses scripts to resample audio and clean annotations that are full of punctuation, numbers (eg 2 instead of two) and bits of English (like two).

Ingredients:
- a folder of Elan files that haven't really been cleaned fully. At least the annotations are all on one tier. 
- audio files have been recorded in a variety of different sample rates, though they are all WAV files.

Method:
Follow the project setup steps to create the working project space.

Run the resampling task. This will convert all WAV files in the `input/data/` directory (and subfolders) to mono, 16bit 44.1 kHz WAVs.

    /kaldi-helpers# task resample-audio

You should see a log of results like: 

    processing
    [0, 0]input/data/1_1_5.wav
    input/data
    input/data/tmp
    ...

When that has completed, you're ready to run the default Elan process. But hey, what about the text cleaning? Well, that happens as part of this task. The annotation values are changed to lowercase, punctuation is stripped, English words are identified from the NLTK corpus, and also checked against a LanguageIdentifier database.

    /kaldi-helpers# task _run-elan-default

Then, 

    /kaldi-helpers# task _train-test-default

Enjoy.


# SILENCE!

This recipe is useful for when there are words in recordings (that have corresponding ELAN transcriptions) that you want to exclude from the training process for whatever reason. Especially useful when there's a word in the midst of an annotation that you don't want. 

Ingredients:
- audio with some unwanted speech
- transcribed ELAN file
 
Method:
Prepare the data by making a tier in your .eaf named 'Silence' (it could be a reference tier, or a regular annotation tier) and make an annotation on that tier for the region that you want to silence. Note that this annotation can overlap annotations on other tiers. Make as many annotations on that Silence tier as you need. The script uses the start and end times of each annotation to do the sampling, so the value of the annotation doesn't matter, they can even be blank. Keep a copy of your audio, as the silencing isn't reversible.

Prepare the workspace by following the project setup steps. Note that this silencing script currently isn't recursive (hopefully it will be soon). If your corpus has data in subfolders, first move the wav and eafs all into the data directory (watch out for file naming conflicts, be careful not to owerwrite files). 

At the Docker container command prompt, run the silencing task:

    /kaldi-helpers# task silence-audio

The terminal will list all of the .eaf files it finds in the corpus directory (input/data) and if it finds a Silence tier, will show the start-end times of the clip. The script will silence the audio at the corresponding times.

If you see a 'Parsing unknown version of ELAN spec... This could result in errors...' warning, you can ignore it. One of the libraries is expecting an older version of ELAN.

When the script finishes, verify that the audio has been silenced by listening to it. Now you are ready to continue with another workflow.


# The Long Player

This recipe is mainly useful to slice up an ELAN corpus in preparation for Persephone. 

Ingredients: 
- ELAN file with lots of annotations and matching audio file
- to use with Persephone, the annotations should be space separated phonemic transcription

Method:
Set up your project as per the project setup steps. However, instead of making a `data` directory for your files, name it `dirty-data` e.g., `~/asr/input/dirty-data` and put your ELAN and WAV files there. 

Run the split_eaf task:

    /kaldi-helpers# task split-eafs

It will look through your data, and slice up by the annotation start-end times on any tier named 'Phrase'. The tier name is configurable if you edit the Docker container's `Taskvars.yml` file. If you have a corresponding annotation on a 'Silence' ref tier, the annotation will be skipped.

As the script goes through the corpus (this script will dig into subfolders), it will output the annotation information that it finds to the terminal. Audio clips are saved to the `input/data` folder and text files of each annotation value are saved to the `input/output/tmp/label` folder. These two folders can be used as a data set for Persephone (as long as the annotation values suit that process). As a bonus, it will also output a `dirty.json` file of the annotation values to `input/output/tmp`.


# The Transcriber

Importing from Transcriber? This recipe is for you. 

Ingredients:
A corpus of .trs files and .wav files.

Method:
Build the basic project as per the project setup steps. Put your .trs and .wav files into the input/data folder.

Run the trs import task:

    /kaldi-helpers# task _run-trs-default

This task doesn't show as much when it is running, but you should end up with a cleaned JSON file, and move your files into the right places for Kaldi.

When that completes, run the train task

    /kaldi-helpers# task _train-test-default

Done!
