#!/bin/sh

OUTPUT=output
#OUTPUT=/srv/ftp/search-console

DATE=$(date +"%Y%m%d%H%M")

#CW=$(date --date="1 days ago" +"%V")
CW=$(date -v-1d +"%V")

mkdir $OUTPUT/$DATE

for i in $CW 
do

  for query in $(ls input)
  do
    python google-analytics.py ALL $i input/$query > $OUTPUT/$DATE/${query%.*}-$i.csv
  done

done

