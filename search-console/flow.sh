#!/bin/sh

for cc in MY ID PH HK SG TH VN
do

  rm -f $cc.csv

  for i in {1..8}
  do
    python sc.py $cc $i >> $cc.csv
  done

done

