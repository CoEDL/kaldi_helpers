
import argparse
import json
import string
import os



# TODO 
# Deal with things like <silence>


def save_wordlist(data):
	""" Given the
	"""
	pass
	


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

		print(utt['transcript'])


def load_file(filename):
	""" Given a filename load and return the object
	"""
	try:
		with open(filename) as data:
			data = json.load(data)
	except Exception as e:
		print(e)
		print("Could not read file " + filename)
		exit()
	return data

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str,
		help="The input file to clean.")
	args = parser.parse_args()

	data = load_file(args.infile)

	filter_data(data)

	#save_data(data)




if __name__ == '__main__':
	main()