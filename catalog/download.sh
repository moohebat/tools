#!/bin/sh

DATE=$(date +"%Y%m%d%H%M")

#OUTPUT=output
OUTPUT=/srv/ftp/catalog

mkdir $OUTPUT/$DATE

for CC in id hk my ph sg th vn
do

	python catalog.py $CC > $OUTPUT/$DATE/catalog-$CC.csv 2>> $OUTPUT/$DATE/error.log

	head -q -n1 $OUTPUT/$DATE/catalog-$CC.csv > $OUTPUT/$DATE/catalog.csv
done

tail -q -n+2 $OUTPUT/$DATE/catalog-*.csv >> $OUTPUT/$DATE/catalog.csv

