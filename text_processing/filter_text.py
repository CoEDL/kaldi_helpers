""" Given a json file with transcript information this tools can perform 
manipulations including generating word lists.
Optionally provide the output json file name with -j

Usage: python filter_text.py sample.json wordlist.txt 
"""

import argparse
import json
import string
import os
import re


def save_wordlist(wordlist, filename):
	""" Given a list of strings write to file
	"""
	try:
		with open(filename, 'w') as f:
			for word in wordlist:
				f.write(word + '\n')
	except:
		print("Could not write out to file " + filename)
		exit()


def extract_wordlist(data):
	""" Given the data object produce a list of strings of single words
		Returned list is of unique words and sorted
	""" 
	result = []
	for utt in data:
		words = utt.get('transcript').split()
		result.extend(words)
	result = list(set(result))
	result.sort()
	return result

def filter_data(data):
	""" Given a data object remove any transcriptons with undesirable features

	"""
	
	to_remove = string.punctuation + "…" + "’" + "“" + "–" + "”" + "‘"
	special_cases = ["<silence>"]
	cleaned_data = []

	for utt in data:
		trans = utt.get('transcript').lower()
		if trans in special_cases:
			continue  # Ignore
		words = trans.split()
		clean_words = []
		valid_utterance = True
		for word in words:
			# If utterance contains a translation
			if word == '@ENG@':  # Translations / ignore
				#words = words[:words.index(word)]
				break

			# If partial digit, throw out whole utterance
			if bool(re.search(r'\d', word)) and not word.isdigit():
				valid_utterance = False
				break

			# Remove punctuation and bad chars
			for char in to_remove:
				word = word.replace(char, '')

			clean_words.append(word)

		cleaned_trans = ' '.join(clean_words).strip()
		if cleaned_trans == "":
			valid_utterance = False

		if not valid_utterance:   # Something was bad in utterance
			continue

		# Should be a clean valid utterance
		utt['transcript'] = cleaned_trans
		cleaned_data.append(utt)
	return cleaned_data




def _filter_data(data):
	""" Returns a dictionary of words and frequencies
	"""
	raise Exception("Deprecated")
	to_remove = string.punctuation + "…" + "’" + "“" + "–" + "”"
	special_cases = ["<silence>"]
	empty_utts = []
	for utt in data:
		words = utt.get('transcript').split()
		for word in words:
			if word in special_cases:
				empty_utts.append(utt)
			if word == "@ENG@":   ## In abui following is a translation to english
				words = words[:words.index(word)]
				break

		for char in to_remove:
			#word = word.replace(char, '')
			words = [word.replace(char, '') for word in words]

		words = [word for word in words if not bool(re.search(r'\d', word)) and not word.isdigit()]  # Filter digits
		utt['transcript'] = ' '.join(words).lower() #words.join(' ').lower()
		if utt['transcript'].strip() == "":
			empty_utts.append(utt)

	# clean any empty/special case utterances		
	[data.remove(utt) for utt in empty_utts]
	#print(utt['transcript'])


def load_file(filename):
	""" Given a filename load and return the object
	"""
	try:
		with open(filename) as f:
			data = json.load(f)
	except Exception as e:
		print("Could not read file " + filename)
		exit()
	return data

def write_json(data, filename):
	""" Wrtie a data object in json format
	"""
	try:
		with open(filename, 'w') as f:
			json.dump(data, f, ensure_ascii=False, indent = 4)
	except:
		print("Could not write out json file " + filename)
		exit()

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str,
		help="The input file to clean.")
	parser.add_argument("wordlistfile", type=str,
		help="Output word list.")
	parser.add_argument("-j", "--jsonOutput", type=str,
		help="Name of json file to use for cleaned data")
	args = parser.parse_args()

	json_outfile = "{0}_clean.json".format(args.infile.rstrip('.json'))
	if args.jsonOutput:
		json_outfile = args.jsonOutput

	data = load_file(args.infile)

	print("Filtering...", end='', flush=True)
	data = filter_data(data)  # mutates the data object
	print("Done.")

	print("Wordlist...", end='', flush=True)
	wordlist = extract_wordlist(data)
	print("Done.")

	print("Write out wordlist and json...", end='', flush=True)
	save_wordlist(wordlist, args.wordlistfile)
	write_json(data, json_outfile)
	print("Done.")




if __name__ == '__main__':
	main()