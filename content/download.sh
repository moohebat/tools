#!/bin/sh
# npm install -g elasticdump

DATE=$(date +"%Y%m%d%H%M")
DB=https://search-iprice-production-6-kqdyyfrc7tpaznra3ahtmgalwa.ap-southeast-1.es.amazonaws.com

mkdir /srv/ftp/content/$DATE/
rm -f input/*.json

for CC in id hk my ph sg th vn
do

	elasticdump --input=$DB/content_$CC --output=input/$CC.json --type=data --searchBody '{ "query" : { "filtered" : { "filter" : { "bool" : { "must" : { "exists" : { "field": "url" } }, "should" : [ { "exists" : { "field": "text" } }, { "exists" : { "field": "shortText" } }, { "exists" : { "field": "sideText" } } ] } }, "query" : { "bool" : { "should" : [ { "bool" : { "must_not" : { "term" : { "text": "" } } } }, { "bool" : { "must_not" : { "term" : { "shortText": "" } } } }, { "bool" : { "must_not" : { "term" : { "sideText": "" } } } } ] } } } }, "fields" : ["url", "text", "shortText", "sideText", "source.brand", "source.category", "source.gender", "source.model", "source.series", "source.color" ]}' --limit=1000

	./content.py input/$CC.json > /srv/ftp/content/$DATE/$CC.csv

done

