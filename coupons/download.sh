#!/bin/sh
# npm install -g elasticdump

DB=https://search-iprice-production-7-pluvqb7oq6wnsisr4k6j62qtlq.ap-southeast-1.es.amazonaws.com
DATE=$(date +"%Y%m%d%H%M")

#OUTPUT=output
OUTPUT=/srv/ftp/coupons

mkdir $OUTPUT/$DATE
rm -f input/*.json

for CC in id hk my ph sg th vn
do

	elasticdump --input=$DB/content_$CC/coupon --output=input/$CC.json --type=data --searchBody '{"query":{"match_all":{}},"fields":["expires","referral","referralMobile","store.url","category.url","popularity"]}' --limit=1000 2>> $OUTPUT/$DATE/error.log

	python coupons.py input/$CC.json > $OUTPUT/$DATE/coupons-$CC.csv 2>> $OUTPUT/$DATE/error.log

	head -q -n1 $OUTPUT/$DATE/coupons-$CC.csv > $OUTPUT/$DATE/coupons.csv
done

tail -q -n+2 $OUTPUT/$DATE/coupons-*.csv >> $OUTPUT/$DATE/coupons.csv

