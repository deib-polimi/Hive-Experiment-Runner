#!/bin/sh

[ "x$(whoami)" = "xhdfs" ] || exec sudo -u hdfs sh "$0"

hdfs dfs -mkdir -p /hdp/apps/2.2.6.0-2800/mapreduce
hdfs dfs -mkdir /hdp/apps/2.2.6.0-2800/hive
hdfs dfs -mkdir /hdp/apps/2.2.6.0-2800/tez

hdfs dfs -put /usr/hdp/2.2.6.0-2800/hadoop/mapreduce.tar.gz /hdp/apps/2.2.6.0-2800/mapreduce
hdfs dfs -put /usr/hdp/2.2.6.0-2800/hive/hive.tar.gz /hdp/apps/2.2.6.0-2800/hive
hdfs dfs -put /usr/hdp/2.2.6.0-2800/tez/lib/tez.tar.gz /hdp/apps/2.2.6.0-2800/tez

hdfs dfs -chmod -R 777 /hdp
hdfs dfs -chmod 555 /hdp/apps/2.2.6.0-2800/mapreduce/mapreduce.tar.gz
hdfs dfs -chmod 555 /hdp/apps/2.2.6.0-2800/hive/hive.tar.gz
hdfs dfs -chmod 555 /hdp/apps/2.2.6.0-2800/tez/tez.tar.gz
