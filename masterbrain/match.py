#!/usr/bin/python

import codecs
import csv
import sys

from elasticsearch import Elasticsearch

reload(sys)
sys.setdefaultencoding("UTF-8")

keywords = []
with codecs.open(sys.argv[1], 'r', 'utf-8') as data_file:
	data = csv.reader(data_file, delimiter=";")

	for line in data:
		if line:
			keywords.append(line[0])

es = Elasticsearch("https://search-iprice-production-3-f3orjkipgmnoxt4qzf6zuervfu.ap-southeast-1.es.amazonaws.com:443")
query = '{"size": 0, "query" : { "term" : { "masterbrain" : "%s" } }}'

for k in keywords:
	ret = es.search("product_*_20160121", "product", query % k.lower())
	hits = ret['hits']['total']

	print k, ";" , hits

