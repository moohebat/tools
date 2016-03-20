#!/bin/sh

for cc in VN
do

  rm -f output/$cc*.csv

  for i in {1..10}
  do
    python search-console.py $cc $i > output/$cc$i.csv
  done

done

