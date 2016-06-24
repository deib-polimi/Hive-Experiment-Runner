#!/bin/sh

## Copyright 2016 Eugenio Gianniti
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

SCRIPT_DIR="${1:?missing script directory}"
CURHOST=$(hostname)

echo "Stop old dstat processes, clean old stats and start sampling system stats on all hosts"

while read host_name; do
  if [ "x${CURHOST}" = "x${host_name}" ]; then
    continue
  fi
  echo "Stopping dstat on ${host_name}"
  < /dev/null ssh -n -f ${CURUSER}@${host_name} "pkill -f '.+/usr/bin/dstat.+'"
done < "${SCRIPT_DIR}/config/hosts.txt"
# Plus localhost
echo "Stopping dstat on $CURHOST"
pkill -f '.+/usr/bin/dstat.+'

while read host_name; do
  if [ "x${CURHOST}" = "x${host_name}" ]; then
    continue
  fi
  echo "Cleaning old dstat log on ${host_name}"
  < /dev/null ssh -n -f ${CURUSER}@${host_name} "rm -f /tmp/*.csv"
done < "${SCRIPT_DIR}/config/hosts.txt"
# Plus localhost
rm -f /tmp/*.csv

while read host_name; do
  if [ "x${CURHOST}" = "x${host_name}" ]; then
    continue
  fi
  echo "Starting dstat on ${host_name}"
  < /dev/null ssh -n -f ${CURUSER}@${host_name} "nohup dstat -tcmnd --output /tmp/stats.${host_name}.csv 5 3000 > /dev/null 2> /dev/null < /dev/null &"
done < "${SCRIPT_DIR}/config/hosts.txt"
#Plus localhost
echo "Starting dstat on $CURHOST"
dstat -tcmnd --output /tmp/stats.${CURHOST}.csv 5 3000 > /dev/null 2> /dev/null < /dev/null &

echo "Done, wait 5 secs to be sure they are all running."
sleep 5s
