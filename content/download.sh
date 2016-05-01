#!/bin/sh
# npm install -g elasticdump
# TODO: downloads some files that are empty
# TODO: in VN 127 text without URL but text

DB=https://search-iprice-production-6-kqdyyfrc7tpaznra3ahtmgalwa.ap-southeast-1.es.amazonaws.com

#for CC in id hk my  ph sg th vn
for CC in vn
do

	elasticdump --input=$DB/content_$CC --output=output/$CC.json --type=data --searchBody '{ "size": 10, "query" : { "filtered" : { "filter" : { "bool" : { "should" : [ { "exists" : { "field": "text" } }, { "exists" : { "field": "shortText" } }, { "exists" : { "field": "sideText" } } ] } }, "query" : { "bool" : { "should" : [ { "bool" : { "must_not" : { "term" : { "text": "" } } } }, { "bool" : { "must_not" : { "term" : { "shortText": "" } } } }, { "bool" : { "must_not" : { "term" : { "sideText": "" } } } } ] } } } }, "fields" : ["store.url", "url", "text", "shortText", "sideText", "source.brand", "source.category", "source.gender", "source.model", "source.series", "source.color" ] }' --limit=1000

done

