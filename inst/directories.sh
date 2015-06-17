#!/bin/sh

sudo -su hdfs

hdfs dfs -mkdir /tmp/ubuntu
hdfs dfs -chmod 777 /tmp/ubuntu
hdfs dfs -chown ubuntu:hdfs /tmp/ubuntu

hdfs dfs -mkdir /user/ubuntu
hdfs dfs -chmod 755 /user/ubuntu
hdfs dfs -chown ubuntu:hdfs /user/ubuntu

exit
