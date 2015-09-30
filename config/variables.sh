#!/bin/bash
# Just some variables useful for other scripts

# Scale size for datagen
SCALE=250
# Number of external iteration for the single query
EXTERNALITER=1
# Number of internal iteration for the single query
INTERNALITER=2
# 1 if we are on policloud and expect latency peaks
ISPOLICLOUD=0
# extension of the query script, typically sql
QUERYEXTENSION=sql
# The hostname of the node hosting the Resource Manager
MASTER=slave10
# A list of queries to execute in the single query run, they are the ones we will execute in the session mode
QUERIES="R1 R2 R3 R4"
# User for ssh-ing into other nodes
CURUSER=ubuntu
# Database to be used
DB_NAME="tpcds_text_$SCALE"
# Path to Resource Manager log file
LOG_PATH=/var/log/hadoop-yarn/yarn/@@RM_LOG@@
# Maximum number of RM logs fetch attempts
FETCH_ATTEMPTS=60
