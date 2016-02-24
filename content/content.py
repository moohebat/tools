#!/usr/bin/python

import codecs
import json
import sys

reload(sys)
sys.setdefaultencoding("UTF-8")

with codecs.open(sys.argv[1], 'r', 'utf-8') as data_file:
	data = json.load(data_file)

for row in data:
	text = 0
	if 'text' in row['_source']:
		if len(row['_source']['text']) > 0:
			text = 1

	shortText = 0
	if 'shortText' in row['_source']:
		if len(row['_source']['shortText']) > 0:
			shortText = 1
	
	if text or shortText:
		if 'url' in row['_source']:
			print row['_index'], row['_source']['url'], row['_type'], text, shortText
