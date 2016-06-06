#!/bin/sh

OUTPUT=~/Downloads/testx.csv
rm -f $OUTPUT

for i in {1..12}
do
  python transactions.py 2015-$i lazada >> $OUTPUT
done

for i in {1..5}
do
  python transactions.py 2016-$i lazada >> $OUTPUT
done
