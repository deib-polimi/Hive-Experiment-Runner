#!/bin/sh

[ "x$(whoami)" = "xhdfs" ] || exec sudo -u hdfs sh "$0"

VERSION=$(ls /usr/hdp | grep -v current)
HDFS_DIR="/hdp/apps/${VERSION}"
OS_DIR="/usr/hdp/${VERSION}"

hdfs dfs -mkdir -p "${HDFS_DIR}/mapreduce"
hdfs dfs -mkdir "${HDFS_DIR}/hive"
hdfs dfs -mkdir "${HDFS_DIR}/tez"

hdfs dfs -put "${OS_DIR}/hadoop/mapreduce.tar.gz" "${HDFS_DIR}/mapreduce"
hdfs dfs -put "${OS_DIR}/hive/hive.tar.gz" "${HDFS_DIR}/hive"
hdfs dfs -put "${OS_DIR}/tez/lib/tez.tar.gz" "${HDFS_DIR}/tez"

hdfs dfs -chmod -R 777 /hdp
hdfs dfs -chmod 555 "${HDFS_DIR}/mapreduce/mapreduce.tar.gz"
hdfs dfs -chmod 555 "${HDFS_DIR}/hive/hive.tar.gz"
hdfs dfs -chmod 555 "${HDFS_DIR}/tez/tez.tar.gz"
