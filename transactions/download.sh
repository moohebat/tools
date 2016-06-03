#!/bin/sh

OUTPUT=~/Downloads/test.csv
rm -f $OUTPUT

for i in {1..12}
do
  python transactions.py 2015-$i all >> $OUTPUT
done

for i in {1..5}
do
  python transactions.py 2016-$i all >> $OUTPUT
done
