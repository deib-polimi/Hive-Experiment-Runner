#!/bin/bash
# FETCH AM and RM logs

source config/variables.sh
CURHOST=$(hostname)

echo "Fetch logs now"

#####################################
# Fetch RM log and populate sessionList.txt #
#####################################
CATTEMPT=1
if [ "$CURHOST" == "$MASTER" ];
then
	echo "Fetching RM log from local (we are on master)"
	tail ${LOG_PATH} -c 20MB > /tmp/log.txt
else
        echo "Fetching RM log from master"
        ssh $MASTER "cat ${LOG_PATH} > /tmp/log.txt"
        scp ${MASTER}:/tmp/log.txt /tmp/log.txt
fi
python logExtractForSession.py ganglia=$GANGLIA_FETCH fetched/session/
PRESULT=$?
while [ $PRESULT -eq 255 ] && [ $CATTEMPT -le 15 ]; do
	sleep 10s
	echo "Trying to fetch log again because end of RM log was not found... Attempt $CATTEMPT"
	if [ "$CURHOST" == "$MASTER" ];
	then
        	echo "Fetching RM log from local (we are on master)"
        	cat ${LOG_PATH} > /tmp/log.txt
	else
        	echo "Fetching RM log from master"
        	ssh $MASTER "cat ${LOG_PATH} > /tmp/log.txt"
        	scp ${MASTER}:/tmp/log.txt /tmp/log.txt
	fi
	python logExtractForSession.py ganglia=$GANGLIA_FETCH fetched/session/
	PRESULT=$?
	CATTEMPT=$(( $CATTEMPT + 1 ))
done

################################
# For every app/session fetch AM log #
###############################
while read line
	do
		appname=$line
		echo "Going to fetch AM logs for $appname"
		yarn logs -applicationId $appname > fetched/session/${appname}.AMLOG.txt
	done < fetched/session/sessionList.txt

####################################
# Merge all dstat logs in a global cluster log #
####################################
python aggregateLog.py /$CURDIR/fetched/session/

echo "Done"

