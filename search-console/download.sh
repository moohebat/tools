#!/bin/sh

DATE=$(date +"%Y%m%d%H%M")

OUTPUT=output
#OUTPUT=/srv/ftp/search-console

# Mac OSX format
CW=$(date -v-3d)
# Linux format
#CW=$(date --date="3 days ago" +"%V")

mkdir $OUTPUT/$DATE

for cc in MY ID HK PH SG TH VN
do

  for i in $CW 
  do
    python search-console.py $cc 2016-$i 10000 > /srv/ftp/search-console/$DATE/10k-$cc-$i.csv 2>> $OUTPUT/$DATE/error.log
  done
  
  cat $OUTPUT/$DATE/10k-$cc-*.csv > $OUTPUT/$DATE/10k-$cc.csv

done

cat $OUTPUT/$DATE/10k-*-*.csv > $OUTPUT/$DATE/10k.csv

