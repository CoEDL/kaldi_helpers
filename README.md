# asr-daan
A repository to hold code produced during the CoEDL working on speech processing for small resource languages.

# Workflow

![ASR pipeline](https://g.gravizo.com/svg?
 digraph G {
  f1 [label="Format 1: Elan"]
    f2 [label="Format 2: Transcriber"]
  f3 [label="Format 3: Praat"]
   conversion [shape="box", label="Conversion", fontsize="20"]
   standard   [shape="box", label="Standard format. JSON file"]
   normalise  [shape="box", label="Normalisation", fontsize="20"]
   norm_model [label="Normalisation rules"]
   pronunciation [shape="box", label="Pronunication", fontsize="20"]
   pron_model [label="Pronunciation rules"]
   kaldi      [shape="box", label="Kaldi", fontsize="20"]
   \
   f1 -> conversion
   f2 -> conversion
   f3 -> conversion
   conversion -> standard
   standard -> normalise [label="TEXT", fontcolor="green"]
   standard -> kaldi [label="AUDIO", fontcolor ="green"]
   norm_model -> normalise
   normalise -> pronunciation
   pron_model -> pronunciation
   pronunciation -> kaldi
   \
   ;}')
