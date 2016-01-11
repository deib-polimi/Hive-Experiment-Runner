#!/bin/bash
# Start/Stop ComputeNodes via Ambari

# SETUP
USER='admin'
PASS='admin' # clusterone
CLUSTER='MasterOfClusters'
AMBARI="master:8080"
# Using $1 directly doesn't work
TARGET=$1

function start () {
  curl -u $USER:$PASS -i -H 'X-Requested-By: ambari' -X PUT -d \
  '{"HostRoles": {"state": "STARTED"}, "RequestInfo": {"context": "Started '"$TARGET"' via REST"}, "Body": {"ServiceInfo": {"state": "STARTED"}}}' \
  http://$AMBARI/api/v1/clusters/$CLUSTER/hosts/$TARGET/host_components/NODEMANAGER
}

function stop () {
  curl -u $USER:$PASS -i -H 'X-Requested-By: ambari' -X PUT -d \
  '{"HostRoles": {"state": "INSTALLED"}, "RequestInfo": {"context": "Stopped '"$TARGET"' via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' \
  http://$AMBARI/api/v1/clusters/$CLUSTER/hosts/$TARGET/host_components/NODEMANAGER
}

### MAIN ###

if [ $# -lt 2 ]; then
  echo "Usage: $0 [target] [stop|start]" >&2
  exit 1
fi

flag=0
if [ $2 = 'stop' ]; then
  while [ $flag -ne 1 ]; do
    if [[ ! -z $(echo `stop` | grep "200 OK") ]]; then
      flag=1
      echo "$2 correctly STOPPED"
    else
      echo "STOP: checkin' in 15s ..."
      sleep 15s
    fi
  done
elif [ $2 = 'start' ]; then
  while [ $flag -ne 1 ]; do
    if [[ ! -z $(echo `start` | grep "200 OK") ]]; then
      flag=1
      echo "$2 correctly STARTED"
    else
      echo "START: checkin' in 30s ..."
      sleep 30s
    fi
  done
else
  echo 'ERROR - BAD REQUEST'
  exit 1
fi
