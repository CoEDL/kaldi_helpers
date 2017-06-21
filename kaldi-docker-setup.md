# Setting up Kaldi using Docker

## Install Docker

- OS X: [https://docs.docker.com/docker-for-mac/install/](https://docs.docker.com/docker-for-mac/install/)
- Windows: [https://docs.docker.com/docker-for-windows/install/](https://docs.docker.com/docker-for-windows/install/)
- Linux (Ubuntu): [https://docs.docker.com/engine/installation/linux/ubuntu/](https://docs.docker.com/engine/installation/linux/ubuntu/)

## Start the Docker app

Once the Docker daemon is running, open up a Terminal/Command Prompt window and type:

```
docker --version
```

## Pull the `coedl/kaldi-srilm` container

```
docker pull coedl/kaldi-srilm
```

## Clone/pull the latest `jotia1/asr-daan` repository from GitHub

I'm going to clone it into a folder called `asr-sandbox` on the Desktop.

```
# mkdir ~/Desktop/asr-sandbox
# cd ~/Desktop/asr-sandbox
git clone https://github.com/jotia1/asr-daan
```

## Run the docker image

**Note the `-v` option** which mounts your local `asr-daan/pronunciation/kaldi-demo-prep/digits` mounted into the Docker container's `/kaldi/egs/digits`

```
docker run -it --rm -v ~/Desktop/asr-sandbox/asr-daan/pronunciation/kaldi-demo-prep/digits/:/kaldi/egs/digits coedl/kaldi-srilm
```

## Execute `run.sh`

Change the directory (`cd`) to the place where the digits directoy had been mounted (the path after Docker `-v` in the command above), then run the Kaldi run script (`./run.sh`).

```
cd /kaldi/egs/digits
./run.sh
```
