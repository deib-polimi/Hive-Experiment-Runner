#!/bin/sh

## Copyright 2015 Eugenio Gianniti
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

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
