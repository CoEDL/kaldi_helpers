""" Given a json file with transcript information this tools can perform 
manipulations including generating word lists.

Usage: python filter_text.py sample.json wordlist.txt
"""

import argparse
import json
import string
import os



# TODO 
# Deal with things like <silence>


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
	""" Note this mutates data
	"""
	to_remove = string.punctuation
	for utt in data:
		words = utt.get('transcript').split()
		for char in to_remove:
			#word = word.replace(char, '')
			words = [word.replace(char, '') for word in words]
		utt['transcript'] = ' '.join(words).lower() #words.join(' ').lower()

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
	args = parser.parse_args()

	data = load_file(args.infile)

	filter_data(data)  # mutates the data object

	wordlist = extract_wordlist(data)

	save_wordlist(wordlist, args.wordlistfile)

	json_outfile = "{0}_clean.json".format(args.infile.rstrip('.json'))
	write_json(data, json_outfile)




if __name__ == '__main__':
	main()