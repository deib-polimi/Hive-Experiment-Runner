#!/bin/bash
# Just some variables useful for other scripts

# Scale size for datagen
SCALE=4
# Number of external iteration for the single query
EXTERNALITER=1
# Number of internal iteration for the single query
INTERNALITER=2
# 1 if we are on policloud and expect latency peaks
ISPOLICLOUD=0
# extension of the query script, typically sql
QUERYEXTENSION=sql
# The hostname of the master node (to fetch Ganglia csv files)
MASTER=slave1
# A list of queries to execute in the single query run, they are the ones we will execute in the session mode
QUERIES="Q3"
# User for ssh-ing into other nodes
CURUSER=ubuntu
# Database to be used
DB_NAME="tpcds_text_$SCALE"
# Path to Resource Manager log file
LOG_PATH=/var/log/hadoop-yarn/yarn/yarn-yarn-resourcemanager-ip-172-31-28-226.log
# Host _hosting_ HiveServer2
HIVE_SERVER2=slave2
