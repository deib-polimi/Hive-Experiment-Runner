#!/bin/bash
# Start/Stop ComputeNodes via Ambari

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
UPPER_DIR=$(dirname "${SCRIPT_DIR}")

. "${UPPER_DIR}/config/variables.sh"
TARGET="$1"

function turnon () {
  curl -u "${AMBARI_USER}":"${AMBARI_PASSWD}" -i -H 'X-Requested-By: ambari' -X PUT -d \
    '{"HostRoles": {"state": "STARTED"}, "RequestInfo": {"context": "Start '"$TARGET"' via REST"}, "Body": {"ServiceInfo": {"state": "STARTED"}}}' \
    http://$AMBARI/api/v1/clusters/$CLUSTER/hosts/$TARGET/host_components/NODEMANAGER
}

function turnoff () {
  curl -u "${AMBARI_USER}":"${AMBARI_PASSWD}" -i -H 'X-Requested-By: ambari' -X PUT -d \
    '{"HostRoles": {"state": "INSTALLED"}, "RequestInfo": {"context": "Stop '"$TARGET"' via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' \
    http://$AMBARI/api/v1/clusters/$CLUSTER/hosts/$TARGET/host_components/NODEMANAGER
}


if [ $# -ne 2 ]; then
  echo "Usage: $0 [target] [turnoff|turnon]" >&2
  exit 1
fi

### TODO: all these requests are not needed, you just read the JSON response
###       and extract an URL to track completion
flag=0
if [ "x$2" = 'xturnoff' ]; then
  while [ $flag -ne 1 ]; do
    if [[ ! -z $(turnoff 2> /dev/null | grep "200 OK") ]]; then
      flag=1
      echo "$TARGET correctly switched off"
    else
      echo "STOP: checking in 15 s"
      sleep 15s
    fi
  done
elif [ "x$2" = 'xturnon' ]; then
  while [ $flag -ne 1 ]; do
    if [[ ! -z $(turnon 2> /dev/null | grep "200 OK") ]]; then
      flag=1
      echo "$TARGET correctly switched on"
    else
      echo "START: checking in 30 s"
      sleep 30s
    fi
  done
else
  echo 'ERROR - BAD REQUEST' >&2
  exit 1
fi
