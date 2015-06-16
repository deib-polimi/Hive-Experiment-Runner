#!/bin/bash
# BUILD deps - START dstat - RUN sessions - STOP dstat - FETCH stats

# These are supposed to be all the queries also present in runSession.py

source variables.sh

CURHOST=$(hostname)

#################################################
# Remove possible previous data from other session runs #
#################################################
echo "Removing old session records"
rm -r -I fetched/session/
rm -f stopSession.tmp
mkdir -p fetched/session

###########################################
# Get query explain from hive to build dependencies #
###########################################
for QUERY in ${QUERIES}
do
	if [ ! -f fetched/session/${QUERY}_dependencies.bin ] && [ ! -f fetched/$QUERY/dependencies.bin ]; then
		q=$(cat $CURDIR/queries/${QUERY}.$QUERYEXTENSION)
		explain_query="explain ${q}"
		echo "$explain_query" > deleteme.tmp
		echo "Get query explain from hive..."
		foo=$(hive -i $CURDIR/queries/my_init.sql -f deleteme.tmp)
		echo "$foo" > deleteme.tmp
		python buildDeps.py deleteme.tmp fetched/session/${QUERY}_dependencies.bin
		echo "Dependencies loaded in fetched/session/${QUERY}_dependencies.bin"
		rm deleteme.tmp
	else
		echo "Using dependency file from single query analysis..."
		cp fetched/$QUERY/dependencies.bin fetched/session/${QUERY}_dependencies.bin
	fi
done

######################################################################
# Start dstat on all hosts after closing possible other instances and cleaning old stats #
######################################################################
echo "Stop old dstat processes, clean old stats and start sampling system stats on all hosts"
#ansible cumpa -a "pkill -f '.+/usr/bin/dstat.+'"
#ansible cumpa -a "rm -f /tmp/*.csv"

while read line
	do
		host=$line
		if [ "$CURHOST" == "$host" ]
		then
			continue
		fi
		echo "Stopping dstat on $host"
		< /dev/null ssh -n -f ${CURUSER}@$host "pkill -f '.+/usr/bin/dstat.+'"
 	done < hosts.txt
# Plus localhost
echo "Stopping dstat on $CURHOST"
pkill -f '.+/usr/bin/dstat.+'


while read line
        do
                host=$line
                if [ "$CURHOST" == "$host" ]
                then
                        continue
                fi
                echo "Cleaning old dstat log on $host"
		< /dev/null ssh -n -f ${CURUSER}@$host "rm -f /tmp/*.csv"
        done < hosts.txt
# Plus localhost
echo "Cleaning old dstat log on $CURHOST"
rm -f /tmp/*.csv


while read line
        do
                host=$line
                if [ "$CURHOST" == "$host" ]
                then
                        continue
                fi
                echo "Starting dstat on $host"
                < /dev/null ssh -n -f ${CURUSER}@$host "nohup dstat -tcmnd --output /tmp/stats.$host.csv 5 3000 > /dev/null 2> /dev/null < /dev/null &"
        done < hosts.txt
# Plus localhost
echo "Starting dstat on $CURHOST"
dstat -tcmnd --output /tmp/stats.${CURHOST}.csv 5 3000 > /dev/null 2> /dev/null < /dev/null &



##################
# Running sessions #
##################

while read line
        do
                arguments=$line
                echo "Running session: ${arguments}"
		nohup python runSessionSingle.py $arguments > /dev/null 2> /dev/null < /dev/null &
        done < ssdata.txt

read -p "Press [Enter] key to stop iterating sessions..."
touch stopSession.tmp

read -p "Check sessions shut down properly, then press [Enter] key to proceed..."


###############
# Stopping dstat #
###############
echo "Stopping dstat on all hosts"
# Since ansible is not working with dstat, let's use ssh iteratively
while read line
        do
                host=$line
                if [ "$CURHOST" == "$host" ]
                then
                        continue
                fi
                echo "Stopping dstat on $host"
                < /dev/null ssh -n -f ${CURUSER}@$host "pkill -f '.+/usr/bin/dstat.+'"
        done < hosts.txt
# Plus localhost
echo "Stopping dstat on $CURHOST"
pkill -f '.+/usr/bin/dstat.+'


echo "Done, wait 5 secs to be sure they all stopped."
sleep 5s

###############################################################################################
# Get all the stat only once at the end of everything, later we will take care of considering the time splits for each app #
###############################################################################################
echo "Fetch stats now"

while read line
        do
                host=$line
                if [ "$CURHOST" == "$host" ]
                then
                        continue
                fi
                echo "Fetching dstat stats from $host"
                < /dev/null scp ${CURUSER}@$host:/tmp/stats.$host.csv fetched/session/
        done < hosts.txt
# Plus localhost
echo "Fetching dstat stats from $CURHOST"
cp /tmp/stats.${CURHOST}.csv fetched/session/

echo "Done, check that dstat files are properly populated"

