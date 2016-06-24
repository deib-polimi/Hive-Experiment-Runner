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
DEST_DIR="${2:?missing destination directory}"
CURHOST=$(hostname)

echo "Stopping dstat on all hosts"
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

echo "Done, wait 10 secs to be sure they all stopped."
sleep 10s

echo "Fetch stats now"
while read host_name; do
  if [ "x${CURHOST}" = "x${host_name}" ]; then
    continue
  fi
  echo "Fetching dstat stats from ${host_name}"
  < /dev/null scp ${CURUSER}@${host_name}:/tmp/stats.${host_name}.csv "${DEST_DIR}"
done < "${SCRIPT_DIR}/config/hosts.txt"
#Plus localhost
echo "Fetching dstat stats from $CURHOST"
cp /tmp/stats.${CURHOST}.csv "${DEST_DIR}"

python "${SCRIPT_DIR}/aggregateLog.py" "${DEST_DIR}"
