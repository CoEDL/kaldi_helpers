export PYTHONIOENCODING="utf-8"

task clean-output-folder tmp-makedir make-kaldi-subfolders

# Extract all tiers from ELAN files

## Note the output file path: remember that this script is being called
## from /src, so we're going to use absolute paths to make everything clear
task elan-to-json > /kaldi-helpers/input/output/tmp/komnzo_all.json

# Select text tiers (starting with tx@), and filter out annotations
# with non-conforming characters
cat input/output/tmp/komnzo_all.json | jq 'map(select(.tier | startswith("tx@")))
	| map(select(.transcript | contains(".") == false))
	| map(select(.transcript | contains(",") == false))
	| map(select(.transcript | contains("#") == false))
	| map(select(.transcript | contains("-") == false))
	| map(select(.transcript | contains("\"") == false))' > /kaldi-helpers/input/output/tmp/komzo_tx_only.json

CLEANED_FILTERED_DATA=komzo_tx_only.json \
	MFCC_SAMPLE_FREQUENCY=48000 \
	task _build-default

