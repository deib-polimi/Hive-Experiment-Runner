#!/bin/bash
# Start/Stop ComputeNodes via Ambari

# SETUP
USER='admin'
PASS='admin'
CLUSTER='MasterOfClusters'
AMBARI="master:8080"
TARGET="$1"

function turnon () {
  curl -u $USER:$PASS -i -H 'X-Requested-By: ambari' -X PUT -d \
    '{"HostRoles": {"state": "STARTED"}, "RequestInfo": {"context": "Start '"$TARGET"' via REST"}, "Body": {"ServiceInfo": {"state": "STARTED"}}}' \
    http://$AMBARI/api/v1/clusters/$CLUSTER/hosts/$TARGET/host_components/NODEMANAGER
}

function turnoff () {
  curl -u $USER:$PASS -i -H 'X-Requested-By: ambari' -X PUT -d \
    '{"HostRoles": {"state": "INSTALLED"}, "RequestInfo": {"context": "Stop '"$TARGET"' via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' \
    http://$AMBARI/api/v1/clusters/$CLUSTER/hosts/$TARGET/host_components/NODEMANAGER
}

### MAIN ###

if [ $# -lt 2 ]; then
  echo "Usage: $0 [target] [turnoff|turnon]" >&2
  exit 1
fi

flag=0
if [ "x$2" = 'xturnoff' ]; then
  while [ $flag -ne 1 ]; do
    if [[ ! -z $(turnoff | grep "200 OK") ]]; then
      flag=1
      echo "$2 correctly STOPPED"
    else
      echo "STOP: checking in 15 s"
      sleep 15s
    fi
  done
elif [ "x$2" = 'xturnon' ]; then
  while [ $flag -ne 1 ]; do
    if [[ ! -z $(turnon | grep "200 OK") ]]; then
      flag=1
      echo "$2 correctly STARTED"
    else
      echo "START: checking in 30 s"
      sleep 30s
    fi
  done
else
  echo 'ERROR - BAD REQUEST' >&2
  exit 1
fi
