#!/bin/sh
# npm install -g elasticdump

DB=https://search-iprice-production-6-kqdyyfrc7tpaznra3ahtmgalwa.ap-southeast-1.es.amazonaws.com

for CC in id hk my ph sg th vn
do

	elasticdump --input=$DB/content_$CC --output=output/$CC.json --type=data --searchBody '{ "query" : { "filtered" : { "filter" : { "bool" : { "must" : { "exists" : { "field": "url" } }, "should" : [ { "exists" : { "field": "text" } }, { "exists" : { "field": "shortText" } }, { "exists" : { "field": "sideText" } } ] } }, "query" : { "bool" : { "should" : [ { "bool" : { "must_not" : { "term" : { "text": "" } } } }, { "bool" : { "must_not" : { "term" : { "shortText": "" } } } }, { "bool" : { "must_not" : { "term" : { "sideText": "" } } } } ] } } } }, "fields" : ["url", "text", "shortText", "sideText", "source.brand", "source.category", "source.gender", "source.model", "source.series", "source.color" ]}' --limit=1000

done

