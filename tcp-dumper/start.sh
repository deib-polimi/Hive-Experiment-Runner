#!/bin/sh

## Copyright 2016 Domenico Enrico Contino, Eugenio Gianniti
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

SCRIPT_DIR="${1:?missing scripts directory}"
DEST_DIR="${2:?missing destination directory}"
CURHOST=$(hostname)

#########################################
# Stop then starts tcpdump on all hosts #
#########################################
echo "Stopping old tcpdump processes..."
while read host_name; do
  if [ "x${CURHOST}" != "x${host_name}" ]; then
    echo "Stopping tcpdump on ${host_name}"
    ssh -fn $CURUSER@$host_name "sudo sh -c 'pkill -f tcpdump' 2> /dev/null < /dev/null &"
  fi
done < "${SCRIPT_DIR}/config/hosts.txt"
# Plus localhost
sudo pkill -f tcpdump 2> /dev/null < /dev/null &

echo "Starting tcpdump on all hosts..."
while read host_name; do
  if [ "x${CURHOST}" != "x${host_name}" ]; then
    echo "Starting tcpdump on ${host_name}"
    ssh -fn ${CURUSER}@${host_name} "sudo nohup tcpdump -q -i eth0 -s 128 host ${host_name} > /tmp/dump.${host_name}.log 2> /dev/null < /dev/null &"
  fi
done < "${SCRIPT_DIR}/config/hosts.txt"
# Plus localhost
echo "Starting tcpdump on ${CURHOST}"
sudo tcpdump -q -i eth0 host -s 128 ${host_name} > "${DEST_DIR}/dump.${CURHOST}.log" 2> /dev/null < /dev/null &
