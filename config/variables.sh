#!/bin/bash
# Just some variables useful for other scripts

# Scale size for datagen
SCALE=250
# Number of external iteration for the single query
EXTERNALITER=1
# Number of internal iteration for the single query
INTERNALITER=2
# 1 if we are on policloud and expect latency peaks
ISPOLICLOUD=1
# extension of the query script, typically sql
QUERYEXTENSION="sql"
# The hostname of the master node (to fetch Ganglia csv files)
MASTER="master.mbarenet.it"
# A list of queries to execute in the single query run, they are the ones we will execute in the session mode
QUERIES="Q6"

CURUSER="gibbo"

DB_NAME="tpcds_text_250"

# Next lines will be parsed by python scripts, it's not a comment!
#% hiveserver2_address slave7.mbarenet.it
#% database_name tpcds_text_250
#% log_path /var/log/hadoop-yarn/yarn/yarn-yarn-resourcemanager-master.mbarenet.it.log
#% fetch_ganglia_metrics true
#% ganglia_interval 15
#% ganglia_base_prefix http://master.mbarenet.it/ganglia/graph.php?r=hour&z=mobile&mobile=1&h=
#% ganglia_base_inter &c=HDPSlaves&g=
#% ganglia_base_suffix &csv=1
#% ganglia_global_prefix http://master.mbarenet.it/ganglia/graph.php?r=hour&z=xlarge&me=HDP_GRID&m=load_one&s=by+name&mc=2&g=
#% ganglia_metrics cpu_report mem_report network_report
#% queues_target_url_prefix http://master.mbarenet.it/ganglia/graph.php?r=hour&z=xlarge&c=HDPResourceManager&h=master.mbarenet.it&jr=&js=&v=0&m=yarn.QueueMetrics.Queue%3D
#% target_queues root.default
#% queues_target_url_suffix .AllocatedContainers&csv=1
#% YEAR 2015
#% GANGLIA_SAMPLE_RATE 15
#% DSTAT_SAMPLE_RATE 5
#@ gibbo query3 queue1
#@ colzada query94 queue2
