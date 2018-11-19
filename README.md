# CoEDL Kaldi pipeline

A set of scripts to use in preparing a corpus for speech-to-text processing with the [Kaldi](http://kaldi-asr.org/) Automatic Speech Recognition Library.

Read about [setting up Docker](docs/guides/kaldi-docker-setup.md) to run all this.

For more information about data requirements, see the [data guide](docs/guides/2018-workshop-preparation.md).

This library uses the  about the [tasks](docs/guides/about-the-tasks.md) that can be run.

## Requirements
This pipeline relies on Python 3.6 and several open-source Python packages (listed [here](./requirements.txt)).
It also assumes you have Kaldi, sox and [task](https://taskfile.org/) installed. We highly recommend using [our docker image](docs/guides/kaldi-docker-setup.md).

## Tasks
Once you've set up kadi_helpers, you can run the various pipeline tasks we've developed. You can read about these [here](docs/guides/about-the-tasks.md). 


## Workflow
<p align="center">
  <img src="docs/img/elpis-pipeline.svg"/>
</p>