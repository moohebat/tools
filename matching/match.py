#!/usr/bin/python

import argparse, codecs, datetime, re, sys, unidecode
from progress.bar import Bar

reload(sys)
sys.setdefaultencoding("UTF-8")

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('masterbrain', type=str, help=('Masterbrain File'))
argparser.add_argument('keywords', type=str, help=('Keyword File'))

def read(filename):
	content = []
	with codecs.open(filename, 'r', 'utf8') as data:
		for line in data:
			if line:
				content.append(line.strip().lower())
	return content

def main(argv):
	args = argparser.parse_args()

	print >> sys.stderr, '# Start: Matching: %s' % (datetime.datetime.now().time().isoformat())

	masterbrain = read(args.masterbrain)
	keywords = read(args.keywords)

	bar = Bar('Processing', max=len(masterbrain), suffix ='%(percent).1f%% - %(eta)ds')

	regex = {}
	for keyword in keywords:
		regex[keyword] = re.compile(r'\b({0})\b'.format(keyword))

	matches = 0
	for string in masterbrain:
		for keyword in keywords:
			if regex[keyword].search(string):
				matches = matches + 1
				break
		else:
			print >> sys.stderr, matches, string
		bar.next()

	bar.finish()

	print matches, "/", len(masterbrain)

	print >> sys.stderr, '# End: Matching: %s' % (datetime.datetime.now().time().isoformat())

if __name__ == '__main__':
    main(sys.argv)
