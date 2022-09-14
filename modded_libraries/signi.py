# -*- coding: utf-8 -*-
"""
	Singi
	~~~~~
	A simple DRAE definitons tool
"""

import requests
from lxml import html
from optparse import OptionParser


def get_word_page(word, url='http://dle.rae.es/srv/search?w='):
	res = requests.get(url + word)
	if res.ok:
		return html.fromstring(res.text)


def get_n_defs(page, n):
	uses = page.xpath('//article')
	uses_definitons = [
		x.xpath(".//p[starts-with(@class,'j')]")[:n] if n != 0 else x.xpath(".//p[starts-with(@class,'j')]")
		for x in uses]
	defs = '<SEP>'.join(
		use.text_content()
		for e in uses_definitons
		for use in e).split('<SEP>')
	return defs


def get_defs(word, limit=0):
	page = get_word_page(word)
	if page is not None:
		defs = get_n_defs(page, limit)
		return defs
	return "N/A :("


def format_output(word_defs):
	return '\n'.join(
		"\t".join(word_def)
		for word_def in
		word_defs.items())


def get_defs_from_words(words):
	word_defs = {
		word: get_defs(word)
		for word in words}
	return format_output(word_defs)


def get_defs_from_file(path):
	with open(path) as file_:
		words = (x.strip() for x in file_.readlines())
	return get_defs_from_words(words)


def main():
	parser = OptionParser(
		version='%prog 1.0',
		description='A simple DRAE definitions tool')
	parser.add_option('-f', '--file', dest='input_file',
					  help='the file to read from')
	parser.add_option('-w', '--word', dest='word',
					  help='the single word to define')
	parser.add_option('-d', '--dest', dest='output_file',
					  help='the file to write to')
	(options, args) = parser.parse_args()

	if options.input_file and options.word:
		parser.error('options --word and --file are mutually exclusive')
	elif not (options.input_file or options.word):
		parser.error('must specify either an input file or a word to define')

	output = None
	if options.input_file is not None:
		output = get_defs_from_file(options.input_file)
	elif options.word is not None:
		output = get_defs_from_words([options.word])

	if options.output_file is not None:
		with open(options.output_file, 'w') as f:
			f.write(output)
	else:
		print(output)

if __name__ == '__main__':
	main()
