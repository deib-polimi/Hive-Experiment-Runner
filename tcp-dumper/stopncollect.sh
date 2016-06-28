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

. "${SCRIPT_DIR}/config/variables.sh"

###############################################################
# Stop then starts tcpdump on all hosts declared in hosts.txt #
###############################################################
echo "Stopping tcpdump on all hosts..."
while read host_name; do
  if [ "x${CURHOST}" != "x${host_name}" ]; then
    echo "Stopping tcpdump on ${host_name}"
    ssh -fn ${CURUSER}@${host_name} "sudo sh -c 'pkill -f tcpdump' 2> /dev/null < /dev/null &"
  fi
done < "${SCRIPT_DIR}/config/hosts.txt"
# Plus localhost
echo "Stopping tcpdump on ${CURHOST}..."
sudo pkill -f tcpdump 2> /dev/null < /dev/null &

echo "Waiting 5 seconds to be sure it's all quiet..."
sleep 5s

#########################
# Collect all the dumps #
#########################
echo "Fetching dumps now..."
while read host_name; do
  if [ "x${CURHOST}" != "x${host_name}" ]; then
    echo "Fetching tcpdump dumps from ${host_name}"
    scp ${CURUSER}@${host_name}:"/tmp/dump.${host_name}.log" "${DEST_DIR}"
  fi
done < "${SCRIPT_DIR}/config/hosts.txt"
# No localhost: start.sh writes directly in place

####################################
# Removing dumps from /tmp folders #
####################################
while read host_name; do
  if [ "x${CURHOST}" != "x${host_name}" ]; then
    echo "Cleaning old tcpdump log on ${host_name}"
    < /dev/null ssh -fn ${CURUSER}@${host_name} "rm -f /tmp/dump.*.log"
  fi
done < "${SCRIPT_DIR}/config/hosts.txt"
