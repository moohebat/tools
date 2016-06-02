#!/bin/bash

DATE=$(date +"%Y%m%d%H%M")

#OUTPUT=output
OUTPUT=/srv/ftp/google-analytics

mkdir $OUTPUT/$DATE

# MacOSX format
#CW=$(date -v-1d +"%V")
# Linux format
CW=$(date --date="1 days ago" +"%V")

for query in $(ls input)
do

  for cc in MY ID HK PH SG TH VN
  do
    #for i in $CW
    for i in $(seq 1 $CW) 
    do
      python google-analytics.py $cc 2016-$i input/$query > $OUTPUT/$DATE/${query%.*}-$cc-$i.csv 2>> $OUTPUT/$DATE/errors.log

      head -q -n1 $OUTPUT/$DATE/${query%.*}-$cc-$i.csv > $OUTPUT/$DATE/${query%.*}-$cc.csv
    done

    tail -q -n+2 $OUTPUT/$DATE/${query%.*}-$cc-*.csv >> $OUTPUT/$DATE/${query%.*}-$cc.csv

    head -q -n1 $OUTPUT/$DATE/${query%.*}-$cc.csv > $OUTPUT/$DATE/${query%.*}.csv
  done

  tail -q -n+2 $OUTPUT/$DATE/${query%.*}-*-*.csv >> $OUTPUT/$DATE/${query%.*}.csv

done
