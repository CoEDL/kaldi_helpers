#!/bin/bash

# Original author Joshua Meyer (2016)
# Modified for CTM output by Nicholas Lambourne & CoEDL (2018)

# USAGE:
#    $ kaldi/egs/your-model/your-model-1/gmm-decode.sh
#
#    This script is meant to demonstrate how an already trained GMM-HMM
#    model and its corresponding HCLG graph, build via Kaldi,
#    can be used to decode new audio files.
#

# INPUT:
#    data/
#       infer/          <= auto created based on the already trained model
#           wav.scp
#           utt2spk
#           spk2utt
#           segments
#           ...
#
#    config/            <= created when triphone model is trained
#        mfcc.conf
#
#    exp/
#        tri/
#            final.mdl  <= all copied verbatim from pre-trained triphone model
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
#            1best-fst.tra
#            1best-fst-word-aligned.tra
#            align-words-best.ctm       <= Time aligned output (CTM)
#            align-words-best.eaf       <= ELAN file //TODO



. ./path.sh
# make sure you include the path to the gmm bin(s)
# the following two export commands are what my path.sh script contains:
# export PATH=$PWD/utils/:$PWD/../../../src/bin:$PWD/../../../tools/openfst/bin:$PWD/../../../src/fstbin/:$PWD/../../../src/gmmbin/:$PWD/../../../src/featbin/:$PWD/../../../src/lm/:$PWD/../../../src/sgmmbin/:$PWD/../../../src/fgmmbin/:$PWD/../../../src/latbin/:$PWD/../../../src/nnet2bin/:$PWD:$PATH
# export LC_ALL=C

# CREATE REQUIRED DIRECTORIES
mkdir ./data/infer

# COPY TRAINED MODEL
cp -R ./exp/tri1 ./exp/tri
cp ./data/train/* ./data/infer
rm ./data/infer/text

# CREATE MFCC
steps/make_mfcc.sh --nj 1 data/infer exp/make_mfcc/infer mfcc

# MFCC + DELTAS --> FEATURE VECTORS
# args:
#       -- utt2spk: utterance to speaker mapping
#       trained CMVN: cepstral mean and variance normalisation
#       trained MFCC: mel-frequency cepstral coefficients
#       PIPED INTO add-deltas (adds delta features)
#       args:
#             delta features
apply-cmvn --utt2spk=ark:data/infer/utt2spk \
    scp:mfcc/cmvn_train.scp \
    scp:mfcc/raw_mfcc_train.1.scp ark:- | \
    add-deltas ark:- ark:data/infer/delta-feats.ark

# TRAINED GMM-HMM + FEATURE VECTORS --> LATTICE
# args:
#       -- word symbol table input file specifier
#       model input file specifier
#       FST input file specifier
#       feature input file specifier
#       lattice output file specifier
gmm-latgen-faster \
    --word-symbol-table=exp/tri1/graph/words.txt \
    exp/tri/final.mdl \
    exp/tri/graph/HCLG.fst \
    ark:data/infer/delta-feats.ark \
    ark,t:data/infer/lattices.ark

# LATTICE --> BEST PATH THROUGH LATTICE AS FST
# args:
#       input lattice file specifier
#       output lattice (FST format) file specifier
lattice-1best \
    ark:data/infer/lattices.ark \
    ark,t:data/infer/1best-fst.tra

# LATTICE-FST --> LATTICE W/ WORD BOUNDARIES
# args:
#       word boundaries file specifier
#       model input file specifier
#       FST lattice input file specifier
#       lattice output file specifier
lattice-align-words \
    data/lang/phones/word_boundary.int \
    exp/tri/final.mdl \
    ark,t:data/infer/1best-fst.tra \
    ark,t:data/infer/1best-fst-word-aligned.tra

# LATTICE W/ WORD BOUNDARIES --> CTM FORMAT (INT-WORDS)
# args:
#       aligned linear lattice input file specifier
#       ctm (int) output file specifier
nbest-to-ctm \
    ark,t:data/infer/1best-fst-word-aligned.tra \
    data/infer/align-words-best-intkeys.ctm

# BEST PATH INTERGERS (CTM) --> BEST PATH WORDS (CTM) // TO FIX
# args:
#       mapping of integer keys to words
#       ctm file to change integers to words in
utils/int2sym.pl -f 5- \
    exp/tri/graph/words.txt \
    data/infer/align-words-best-intkeys.ctm \
    > data/infer/align-words-best-wordkeys.ctm

### --> Works up to here

# BEST PATH WORDS (CTM) --> ELAN
# // TODO

# REPORT OUTPUT
echo "CTM output"
cat ./data/infer/align-words-best-wordkeys.ctm
