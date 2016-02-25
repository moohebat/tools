#!/bin/sh

for cc in MY ID PH HK SG TH VN
do

  rm -f $cc.csv

  for i in {1..8}
  do
    python search-console.py $cc $i >> $cc$i.csv
  done

done

