#!/bin/sh

DATE=$(date +"%Y%m%d%H%M")

OUTPUT=output
#OUTPUT=/srv/ftp/search-console

mkdir $OUTPUT/$DATE

# MacOSX format
CW=$(date --date="1 days ago" +"%V")
# Linux format
#CW=$(date -v-1d +"%V")

for query in $(ls input)
do

  for cc in MY ID HK PH SG TH VN
  do
    for i in $CW 
    do
      python google-analytics.py $cc 2016-$i input/$query > $OUTPUT/$DATE/${query%.*}-$cc-$i.csv 2>> $OUTPUT/$DATE/errors.log
    done

    cat $OUTPUT/$DATE/${query%.*}-$cc-*.csv > $OUTPUT/$DATE/${query%.*}-$cc.csv
  done

  cat $OUTPUT/$DATE/${query%.*}-*-*.csv > $OUTPUT/$DATE/${query%.*}.csv

done
