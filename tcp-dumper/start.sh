#!/bin/bash
# Run on master and starts tcpdump logging

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

# SETUP
UPPER_DIR=`dirname ${SCRIPT_DIR}` 
. "${UPPER_DIR}/config/variables.sh"
CURHOST=$(hostname)
QUERY_NAME=$1

#########################################
# Stop then starts tcpdump on all hosts #
#########################################
echo "Stopping old tcpdump processes..."

while read host_name; do
  if [ "x${CURHOST}" != "x${host_name}" ]; then
    echo "Stopping tcpdump on ${host_name}"
    ssh -fn $CURUSER@$host_name "sudo sh -c 'pkill -f tcpdump' 2> /dev/null < /dev/null &"
  fi
done < "${UPPER_DIR}/config/hosts.txt"
# Plus localhost
sudo pkill -f tcpdump 2> /dev/null < /dev/null &
echo "Starting tcpdump on all hosts..."
while read host_name; do
  if [ "x${CURHOST}" != "x${host_name}" ]; then
    echo "Starting tcpdump on ${host_name}"
    ssh -fn $CURUSER@$host_name "sudo nohup tcpdump -q -i eth0 \"udp and host ${host_name}\" > /tmp/dump.${host_name}.log 2> /dev/null < /dev/null &"
  fi
done < "${UPPER_DIR}/config/hosts.txt"
# Plus localhost
echo "Starting tcpdump on $CURHOST" # Definitive master dumps save location
sudo tcpdump -q -i eth0 "udp and host ${CURHOST}" > fetched/${QUERY_NAME}/dump.${QUERY_NAME}.$CURHOST.log 2> /dev/null < /dev/null &
echo "start.sh has finished its job for query ${QUERY_NAME}."
echo
