#!/bin/sh
# npm install -g elasticdump

DB=https://search-iprice-production-7-pluvqb7oq6wnsisr4k6j62qtlq.ap-southeast-1.es.amazonaws.com
DATE=$(date +"%Y%m%d%H%M")

#OUTPUT=output
OUTPUT=/srv/ftp/content

mkdir $OUTPUT/$DATE
rm -f input/*.json

for CC in id hk my ph sg th vn
do

	elasticdump --input=$DB/content_$CC --output=input/$CC.json --type=data --searchBody '{"query":{"filtered":{"filter":{"bool":{"must":{"exists":{"field":"url"}},"should":[{"exists":{"field":"text"}},{"exists":{"field":"shortText"}},{"exists":{"field":"sideText"}},{"exists":{"field":"title"}},{"exists":{"field":"heading"}},{"exists":{"field":"meta"}},{"exists":{"field":"categoryOverview"}},{"exists":{"field":"image"}},{"term":{"_type":"category"}}]}},"query":{"bool":{"should":[{"bool":{"must_not":{"term":{"text":""}}}},{"bool":{"must_not":{"term":{"shortText":""}}}},{"bool":{"must_not":{"term":{"sideText":""}}}},{"bool":{"must_not":{"term":{"title":""}}}},{"bool":{"must_not":{"term":{"heading":""}}}},{"bool":{"must_not":{"term":{"meta":""}}}},{"bool":{"must":{"term":{"categoryOverview":true}}}},{"bool":{"must_not":{"term":{"image":""}}}}]}}}},"fields":["url","text","shortText","sideText","source.brand","source.category","source.gender","source.model","source.series","source.color","title","meta","heading","categoryOverview","image","internationalUrl.HK","internationalUrl.ID","internationalUrl.MY","internationalUrl.PH","internationalUrl.SG","internationalUrl.TH","internationalUrl.VN"]}' --limit=1000 2>> $OUTPUT/$DATE/error.log

	python content.py input/$CC.json > $OUTPUT/$DATE/content-$CC.csv 2>> $OUTPUT/$DATE/error.log

	head -q -n1 $OUTPUT/$DATE/content-$CC.csv > $OUTPUT/$DATE/content.csv
done

tail -q -n+2 $OUTPUT/$DATE/content-*.csv >> $OUTPUT/$DATE/content.csv

