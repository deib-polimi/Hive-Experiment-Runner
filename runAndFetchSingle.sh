#!/bin/bash
# run specified query 100 times and fetch log and stats in an appropriate folder
# A file with all the hosts, line by line, is expected in the same folder



# SETUP
source variables.sh
CURDIR=$(pwd)
CURHOST=$(hostname)

for QUERYNAME in ${QUERIES}
do
	# INIT
	EXTERNALCOUNTER=1
	EXCEED=0

	rm -r -f fetched/$QUERYNAME
	mkdir -p fetched/$QUERYNAME
	# Renewed here and at every external loop, the incremental list is in the queries output folder
	rm -f apps.tmp

	#echo "Sleeping..."
	#sleep 1s

	######################################################################
	# Start dstat on all hosts after closing possible other instances and cleaning old stats #
	######################################################################
	echo "Stop old dstat processes, clean old stats and start sampling system stats on all hosts"
	#ansible cumpa -a "pkill -f '.+/usr/bin/dstat.+'"
	#ansible cumpa -a "rm -f /tmp/*.csv"

	while read line
                do
			host=$line
			if [ "$CURHOST" == "$host" ];
			then
                               	continue
			fi
                        echo "Stopping dstat on $host"
                        < /dev/null ssh -n -f gibbo@$host "pkill -f '.+/usr/bin/dstat.+'"
                done < hosts.txt
        # Plus localhost
	echo "Stopping dstat on $CURHOST"
        pkill -f '.+/usr/bin/dstat.+'

	while read line
                do
                        host=$line
			if [ "$CURHOST" == "$host" ];
                        then
                                continue
                        fi
                        echo "Cleaning old dstat log on $host"
                        < /dev/null ssh -n -f gibbo@$host "rm -f /tmp/*.csv"
                done < hosts.txt
        # Plus localhost
        rm -f /tmp/*.csv


	#ansible cumpa -a "sh /tmp/startdstat.sh"
	#ansible cumpa -a "export THISHOST=$(hostname);dstat -tcmnd --output /tmp/stats.$THISHOST.csv 5 3000 > /dev/null &"
	# Since ansible is not working with dstat, let's use ssh iteratively
	while read line
		do
			host=$line
			if [ "$CURHOST" == "$host" ];
                        then
                                continue
                        fi
			echo "Starting dstat on $host"
			< /dev/null ssh -n -f gibbo@$host "nohup dstat -tcmnd --output /tmp/stats.$host.csv 5 3000 > /dev/null 2> /dev/null < /dev/null &"
		done < hosts.txt
	#Plus localhost
	echo "Starting dstat on $CURHOST"
	dstat -tcmnd --output /tmp/stats.${CURHOST}.csv 5 3000 > /dev/null 2> /dev/null < /dev/null &
	echo "Done, wait 5 secs to be sure they are all running."
	sleep 5s

	while [  $EXTERNALCOUNTER -le $EXTERNALITER ]; do
		COUNTER=1
		rm apps.tmp
		echo "Running external iteration: $EXTERNALCOUNTER"

		###########################################
		# Get query explain from hive to build dependencies #
		###########################################
		if [ ! -f fetched/$QUERYNAME/dependencies.bin ]; then
			q=$(cat $CURDIR/hive-testbench-hive14/sample-queries-tpcds/$QUERYNAME.$QUERYEXTENSION)
			explain_query="explain ${q}"
			echo "$explain_query" > deleteme.tmp
			echo "Get query explain from hive..."
			foo=$(hive -i $CURDIR/hive-testbench-hive14/sample-queries-tpcds/my_init.sql -f deleteme.tmp)
			echo "$foo" > deleteme.tmp
			python buildDeps.py deleteme.tmp fetched/$QUERYNAME/dependencies.bin
			echo "Dependencies loaded in fetched/$QUERYNAME/dependencies.bin"
			rm deleteme.tmp
			else
			echo "Dependencies file already there, skipping..."
		fi


		#############################################################################################
		# Run n times our query, save the application id in apps.tmp and fetched/$QUERYNAME/apps_$QUERYNAME.txt #
		#############################################################################################
		while [  $COUNTER -le $INTERNALITER ]; do
			echo "Running query. Attempt $COUNTER"
			touch start.tmp
			TST=$(date +"%T.%3N")
			hive -i $CURDIR/hive-testbench-hive14/sample-queries-tpcds/my_init.sql -f $CURDIR/hive-testbench-hive14/sample-queries-tpcds/$QUERYNAME.$QUERYEXTENSION &> temp.tmp
			TND=$(date +"%T.%3N")
			touch -d "-120 seconds" end.tmp
			# If the execution of the query took more than 2 minute (usually it takes 50 secs),
			# the cluster could have stalled at some point, ignore this execution
			# Skip this on production
			if [ end.tmp -nt start.tmp ] && [ $ISPOLICLOUD -eq 1 ]; then
				echo "skipping current execution because it took too long"
				EXCEED=$(( $EXCEED + 1 ))
				# Wait 1 minutes for the cluster to recover
				echo "Next attempt in 60s"
				sleep 60s
				continue
			else
				# Look for the application id in the hive output and save it in apps.tmp
				strresult="NONE"

				##########################################
				# Save app name in permanent and temporary file #
				##########################################
				while read -r line
				do
					if [[ $line =~ .*(application_[0-9]+_[0-9]+).* ]];
					then
						strresult=${BASH_REMATCH[1]}
						echo "Finished app: $strresult"
						echo "$strresult" >> fetched/$QUERYNAME/apps_$QUERYNAME.txt
						echo "$strresult" >> apps.tmp
						echo "${strresult}\n${TST}\t${TND}">> fetched/$QUERYNAME/real_start_end.txt
						break
					fi
				done < temp.tmp
			fi
			COUNTER=$(( $COUNTER + 1 ))
		done

		echo "Totally exceeded $EXCEED times"

		############################################################
		# Wait some secs for flushing of previous logs, 2 mins should be enough #
		############################################################
		echo "Waiting 120s for logs to be flushed."
		sleep 120s
		rm -f /tmp/log.txt
		##########################################################
		# For each app, fetch the logs and run the python script to get the time #
		# intervals for our analysis                                                                        #
		##########################################################
		while read line || [[ -n $line ]]; do
			appname=$line
			echo "Going to fetch AM logs for $appname"
			yarn logs -applicationId $appname > fetched/$QUERYNAME/${appname}.AMLOG.txt
			echo "Going to fetch RM logs for $appname"
			CATTEMPT=1
			if [ ! -f /tmp/log.txt ]; then
				if [ "$CURHOST" == "$MASTER" ];
        	                then
                	                echo "Fetching RM log from local (we are on master)"
					tail /var/log/hadoop-yarn/yarn/yarn-yarn-resourcemanager-master.mbarenet.it.log -c 20MB > /tmp/log.txt
               		        else
					echo "Fetching RM log from master"
					< /dev/null ssh $MASTER 'tail /var/log/hadoop-yarn/yarn/yarn-yarn-resourcemanager-master.mbarenet.it.log -c 20MB > /tmp/log.txt'
					< /dev/null scp ${MASTER}:/tmp/log.txt /tmp/log.txt
				fi
			else
				echo "RM already fetched. Moving on..."
			fi
			python logExtract.py $appname fetched/$QUERYNAME/
			PRESULT=$?
			while [ $PRESULT -eq 255 ] && [ $CATTEMPT -le 15 ]; do
				sleep 10s
				if [ "$CURHOST" == "$MASTER" ];
                        	then
                        	        echo "Fetching RM log from local (we are on master)"
                        	        tail /var/log/hadoop-yarn/yarn/yarn-yarn-resourcemanager-master.mbarenet.it.log -c 20MB > /tmp/log.txt
                       		else
					echo "Fetching RM log from master"
	                                < /dev/null ssh $MASTER 'tail /var/log/hadoop-yarn/yarn/yarn-yarn-resourcemanager-master.mbarenet.it.log -c 20MB > /tmp/log.txt'
	                                < /dev/null scp ${MASTER}:/tmp/log.txt /tmp/log.txt
        	                fi
				echo "Trying to fetch log again because end of RM log was not found... Attempt $CATTEMPT"
				python logExtract.py $appname fetched/$QUERYNAME/
				PRESULT=$?
				CATTEMPT=$(( $CATTEMPT + 1 ))
			done

		done < apps.tmp

		rm -f /tmp/log.txt


		EXTERNALCOUNTER=$(( $EXTERNALCOUNTER + 1 ))

	done

	###############################################################################################
	# Get all the stat only once at the end of everything, later we will take care of considering the time splits for each app #
	###############################################################################################
	echo "Stopping dstat on all hosts"
	while read line
		do
			host=$line
			if [ "$CURHOST" == "$host" ];
                        then
                                continue
                        fi
			echo "Stopping dstat on $host"
			< /dev/null ssh -n -f gibbo@$host "pkill -f '.+/usr/bin/dstat.+'"
		done < hosts.txt
	# Plus localhost
	echo "Stopping dstat on $CURHOST"
	pkill -f '.+/usr/bin/dstat.+'

	echo "Done, wait 10 secs to be sure they all stopped."
	sleep 10s

	echo "Fetch stats now"
	while read line
		do
			host=$line
			if [ "$CURHOST" == "$host" ];
                        then
                                continue
                        fi
			echo "Fetching dstat stats from $host"
			< /dev/null scp gibbo@$host:/tmp/stats.$host.csv fetched/$QUERYNAME/
		done < hosts.txt
	#Plus localhost
	echo "Fetching dstat stats from $CURHOST"
	cp /tmp/stats.${CURHOST}.csv fetched/$QUERYNAME/

	echo "Done, check dstat files are properly populated"
	read -p "Press [Enter] key to create dstat aggregated logs..."

	####################################
	# Merge all dstat logs in a global cluster log #
	####################################
	python aggregateLog.py /$CURDIR/fetched/$QUERYNAME/


done
