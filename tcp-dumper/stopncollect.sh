#!/bin/bash
# Run on master, stops and collects all tcpdump logs

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

# SETUP
UPPER_DIR=$(dirname "${SCRIPT_DIR}")
. "${UPPER_DIR}/config/variables.sh"
CURHOST=$(hostname)
QUERY_NAME=$1

#######################################################################
# Stop then starts tcpdump on all hosts declared in tcpdump-hosts.txt #
#######################################################################
echo "Stopping tcpdump on all hosts..."

while read host_name; do
  if [ "x${CURHOST}" != "x${host_name}" ]; then
    echo "Stopping tcpdump on ${host_name}"
    ssh -fn ${CURUSER}@${host_name} "sudo sh -c 'pkill -f tcpdump' 2> /dev/null < /dev/null &"
  fi
done < "${UPPER_DIR}/config/hosts.txt"
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
    scp ${CURUSER}@${host_name}:"/tmp/dump.${host_name}.log" "fetched/${QUERY_NAME}"
  fi
done < "${UPPER_DIR}/config/hosts.txt"

####################################
# Removing dumps from /tmp folders #
####################################
while read host_name; do
  if [ "x${CURHOST}" != "x${host_name}" ]; then
    echo "Cleaning old tcpdump log on ${host_name}"
    < /dev/null ssh -fn ${CURUSER}@${host_name} "rm -f /tmp/dump.*.log"
  fi
done < "${UPPER_DIR}/config/hosts.txt"

echo "$0 has finished its job with query ${QUERY_NAME}"
echo
