export PYTHONIOENCODING="utf-8"

git pull
cd /kaldi-helpers

task clean-output-folder tmp-makedir make-kaldi-subfolders

task elan-to-json > output/tmp/komnzo_all.json

cat output/tmp/komnzo_all.json | jq 'map(select(.tier | startswith("tx@")))
	| map(select(.transcript | contains(".") == false))
	| map(select(.transcript | contains(",") == false))
	| map(select(.transcript | contains("#") == false))
	| map(select(.transcript | contains("-") == false))
	| map(select(.transcript | contains("\"") == false))' > output/tmp/komzo_tx_only.json

task json-to-kaldi < output/tmp/komzo_tx_only.json

cp output/tmp/json_splitted/corpus.txt output/kaldi/data/local/

    # Extract unique wordlist for corpus data, then generate pronunciation dictionary
task make-wordlist < output/tmp/komzo_tx_only.json > output/tmp/corpus_wordlist.txt
LETTER_TO_SOUND=input/komnzo_config.txt task make-prn-dict < output/tmp/corpus_wordlist.txt > output/kaldi/data/local/dict/lexicon.txt

LETTER_TO_SOUND=input/komnzo_config.txt task make-nonsil-phones > output/kaldi/data/local/dict/nonsilence_phones.txt
task copy-silence-phones

cp output/tmp/json_splitted/segments output/tmp/json_splitted/text output/tmp/json_splitted/utt2spk output/tmp/json_splitted/wav.scp output/kaldi/data/test/
cp output/tmp/json_splitted/segments output/tmp/json_splitted/text output/tmp/json_splitted/utt2spk output/tmp/json_splitted/wav.scp output/kaldi/data/train/

task gather-wavs extract-wavs make-conf-files copy-helper-scripts

SAMPLE_FREQUENCY=48000 FRAME_LENGTH=25 LOW_FREQ=20 HIGH_FREQ=22050 NUM_CEPS=7 mo moustache-templates/mfcc.conf > output/kaldi/conf/mfcc.conf
