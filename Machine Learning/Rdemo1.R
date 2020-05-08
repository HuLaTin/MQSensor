#!/bin/bash

CSVONE=fileOne.csv
CSVTWO=fileTwo.csv

R=/usr/bin/R

mkdir -p ./logs

for THRESHOLD in 0.03 0.025 0.1
do
for (( WINDOWSIZE = 25; WINDOWSIZE <= 100; WINDOWSIZE = WINDOWSIZE + 25 ))
  do
OUTDIR=./testRunSets/set-$WINDOWSIZE-$THRESHOLD
mkdir -p $OUTDIR
echo thresh hold $THRESHOLD, window size $WINDOWSIZE, outdir $OUTDIR
echo $R --slave --args $OUTDIR $CSVONE $CSVTWO $THRESHOLD $WINDOWSIZE \< demoCommandLineArgs.r
$R --slave --args $OUTDIR $CSVONE $CSVTWO $THRESHOLD $WINDOWSIZE \
< demoCommandLineArgs.r > ./logs/set-$WINDOWSIZE-$THRESHOLD.log

exit

done

exit

done


###################################################################
exit