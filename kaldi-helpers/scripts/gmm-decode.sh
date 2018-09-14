#!/bin/bash

# Original author Joshua Meyer (2016)
# modified by CoEDLers (2018)

# USAGE:
#    $ kaldi/egs/your-model/your-model-1/gmm-decode.sh
#
#    This script is meant to demonstrate how an existing GMM-HMM
#    model and its corresponding HCLG graph, build via Kaldi,
#    can be used to decode new audio files.
#    Although this script takes no command line arguments, it assumes
#    the existance of a directory (./transcriptions) and an scp file
#    within that directory (./transcriptions/wav.scp). For more on scp
#    files, consult the official Kaldi documentation.

# INPUT:
#    data/
#       infer/          <= these need to be created
#           wav.scp
#           utt2spk
#           spk2utt
#           text        <= put a transcription here for quick comparison against generated one
#
#    config/
#        mfcc.conf
#
#    exp/
#        tri/
#            final.mdl
#
#            graph/
#                HCLG.fst
#                words.txt

# OUTPUT:
#    data/
#       infer/
#            feats.ark
#            feats.scp
#            delta-feats.ark
#            lattices.ark
#            one-best.tra
#            one-best-hypothesis.txt



. ./path.sh
# make sure you include the path to the gmm bin(s)
# the following two export commands are what my path.sh script contains:
# export PATH=$PWD/utils/:$PWD/../../../kaldi-helpers/bin:$PWD/../../../tools/openfst/bin:$PWD/../../../kaldi-helpers/fstbin/:$PWD/../../../kaldi-helpers/gmmbin/:$PWD/../../../kaldi-helpers/featbin/:$PWD/../../../kaldi-helpers/lm/:$PWD/../../../kaldi-helpers/sgmmbin/:$PWD/../../../kaldi-helpers/fgmmbin/:$PWD/../../../kaldi-helpers/latbin/:$PWD/../../../kaldi-helpers/nnet2bin/:$PWD:$PATH
# export LC_ALL=C

# AUDIO --> FEATURE VECTORS
steps/make_mfcc.sh --nj 1 data/infer exp/make_mfcc/infer mfcc

apply-cmvn --utt2spk=ark:data/infer/utt2spk scp:mfcc/cmvn_test.scp scp:mfcc/raw_mfcc_infer.1.scp ark:- | add-deltas ark:- ark:data/infer/delta-feats.ark

# TRAINED GMM-HMM + FEATURE VECTORS --> LATTICE
gmm-latgen-faster \
    --word-symbol-table=exp/tri1/graph/words.txt \
    exp/tri1/final.mdl \
    exp/tri1/graph/HCLG.fst \
    ark:data/infer/delta-feats.ark \
    ark,t:data/infer/lattices.ark

# LATTICE --> BEST PATH THROUGH LATTICE
lattice-best-path \
    --word-symbol-table=exp/tri1/graph/words.txt \
    ark:data/infer/lattices.ark \
    ark,t:data/infer/one-best.tra

# BEST PATH INTERGERS --> BEST PATH WORDS
utils/int2sym.pl -f 2- \
    exp/tri1/graph/words.txt \
    data/infer/one-best.tra \
    > data/infer/one-best-hypothesis.txt

echo ""
echo ""
echo "Reference (human-provided golden transription) / Ref"
cat data/infer/text

echo ""
echo ""
echo "Machine-generated transcription / Hypothesis / Hyp"
cat data/infer/one-best-hypothesis.txt

echo ""
echo ""
