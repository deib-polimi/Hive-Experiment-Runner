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
UPPER_DIR=$(dirname "${SCRIPT_DIR}")
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
    #ssh -fn ${CURUSER}@${host_name} "sudo nohup tcpdump -q -i eth0 host ${host_name} -s 128 'tcp[13] & 8!=0' > /tmp/dump.${host_name}.log 2> /dev/null < /dev/null &"
    ssh -fn ${CURUSER}@${host_name} "sudo nohup tcpdump -q -i eth0 -s 128 host ${host_name} > /tmp/dump.${host_name}.log 2> /dev/null < /dev/null &"

  fi
done < "${UPPER_DIR}/config/hosts.txt"
# Plus localhost
echo "Starting tcpdump on ${CURHOST}" # Final master dumps save location
sudo tcpdump -q -i eth0 host -s 128 ${host_name} > "fetched/${QUERY_NAME}/dump.${CURHOST}.log" 2> /dev/null < /dev/null &

echo "$0 has finished its job with query ${QUERY_NAME}"
echo
