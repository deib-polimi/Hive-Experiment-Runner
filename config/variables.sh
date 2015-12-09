### Change for every experiment ###

# Number of external iteration for the single query
EXTERNALITER=1
# Number of internal iteration for the single query
INTERNALITER=2
# A list of queries to execute in the single query run
QUERIES="R1 R2 R3 R4"


### Cluster-related stuff, change once ###

# TPC-DS dataset scale parameter
SCALE=250
# The hostname of the node hosting the Resource Manager
MASTER=slave10
# User for ssh-ing into other nodes
CURUSER=ubuntu
# Path to Resource Manager log file
LOG_PATH=/var/log/hadoop-yarn/yarn/@@RM_LOG@@


### These should not be changed ###

# Maximum number of RM logs fetch attempts
FETCH_ATTEMPTS=60
# extension of the query script, typically sql
QUERYEXTENSION=sql
# Database to be used
DB_NAME="tpcds_text_$SCALE"
