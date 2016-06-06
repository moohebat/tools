#!/bin/bash

DATE=$(date +"%Y%m%d%H%M")

#OUTPUT=output
OUTPUT=/srv/ftp/transactions/

mkdir $OUTPUT/$DATE

for i in {1..12}
do
  export DISPLAY=:1; python transactions.py 2015-$i all > $OUTPUT/$DATE/transactions-2015-$i.csv 2>> $OUTPUT/$DATE/errors.log
  head -q -n1 $OUTPUT/$DATE/transactions-2015-$i.csv > $OUTPUT/$DATE/transactions-2015.csv
done

tail -q -n+2 $OUTPUT/$DATE/transactions-2015-*.csv >> $OUTPUT/$DATE/transactions-2015.csv
head -q -n1 $OUTPUT/$DATE/transactions-2015.csv > $OUTPUT/$DATE/transactions.csv

for i in {1..5}
do
  export DISPLAY=:1; python transactions.py 2016-$i all > $OUTPUT/$DATE/transactions-2016-$i.csv 2>> $OUTPUT/$DATE/errors.log
  head -q -n1 $OUTPUT/$DATE/transactions-2016-$i.csv > $OUTPUT/$DATE/transactions-2016.csv
done

tail -q -n+2 $OUTPUT/$DATE/transactions-2016-*.csv >> $OUTPUT/$DATE/transactions-2016.csv
head -q -n1 $OUTPUT/$DATE/transactions-2015.csv > $OUTPUT/$DATE/transactions.csv

tail -q -n+2 $OUTPUT/$DATE/transactions-2015.csv >> $OUTPUT/$DATE/transactions.csv
tail -q -n+2 $OUTPUT/$DATE/transactions-2016.csv >> $OUTPUT/$DATE/transactions.csv
