#!/bin/bash

QUERYNAME="Q3"
USERNAME="gribaudo"
QUERYEXTENSION="sql"
QUEUE="queue1"
CURDIR=$(pwd)

rm -f stopSession.tmp
rm -f ${USERNAME}.${QUERYNAME}.${QUEUE}.txt
while [[ ! -f stopSession.tmp ]]; do
  rm -f temp_${QUERYNAME}.tmp
  TST=$(date +"%T.%3N")
  sudo -u $USERNAME hive -i $CURDIR/hinit/${QUEUE}.sql -f $CURDIR/hive-testbench-hive14/sample-queries-tpcds/$QUERYNAME.$QUERYEXTENSION &> temp_${QUERYNAME}.tmp
  TND=$(date +"%T.%3N")
  while read -r line || [[ -n $line ]]; do
    if [[ $line =~ .*(application_[0-9]+_[0-9]+).* ]];
    then
      strresult=${BASH_REMATCH[1]}
      echo "${strresult},${TST},${TND}">> fetched/session/${USERNAME}.${QUERYNAME}.${QUEUE}.txt
      break
    fi
  done < temp_${QUERYNAME}.tmp
  python waitExp.py                
done
