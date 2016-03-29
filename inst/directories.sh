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

hdfs dfs -mkdir /tmp/ubuntu
hdfs dfs -chmod 777 /tmp/ubuntu
hdfs dfs -chown ubuntu:hdfs /tmp/ubuntu

hdfs dfs -mkdir /user/ubuntu
hdfs dfs -chmod 755 /user/ubuntu
hdfs dfs -chown ubuntu:hdfs /user/ubuntu
