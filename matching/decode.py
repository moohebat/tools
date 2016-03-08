#!/usr/bin/python

import argparse, codecs, datetime, sys, unidecode

reload(sys)
sys.setdefaultencoding("UTF-8")

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('filename', type=str, help=('Filename'))

def read(filename):
	content = []
	with codecs.open(filename, 'r', 'utf8') as data:
		for line in data:
			if line:
				content.append(line.strip())
	return content

def decode(string):
	return unidecode.unidecode(string)

def main(argv):
	args = argparser.parse_args()

	keywords = read(args.filename)

	print >> sys.stderr, '# Start: Decode: %s' % (datetime.datetime.now().time().isoformat())

	for keyword in keywords:
		print decode(keyword)

	print >> sys.stderr, '# End: Decode: %s' % (datetime.datetime.now().time().isoformat())

if __name__ == '__main__':
    main(sys.argv)
