#!/bin/sh

DATE=$(date +"%Y%m%d%H%M")
CW=$(date --date="3 days ago" +"%V")

# Mac OSX
# CW=$(date -v-3d)

mkdir /srv/ftp/search-console/$DATE/

for i in $CW 
do

  for cc in MY ID HK PH SG TH VN
  do
    python search-console.py $cc $i 10 > /srv/ftp/search-console/$DATE/$cc-$i-10k.csv
  done

done

