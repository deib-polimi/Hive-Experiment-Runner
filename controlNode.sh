#!/bin/bash
# Start/Stop ComputeNodes via Ambari

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

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
. "${SCRIPT_DIR}/config/variables.sh"

OPERATION="$1"
TARGET="$2"
usage_msg="usage: $0 stop|start target"


turnon () {
  curl -u "${AMBARI_USER}":"${AMBARI_PASSWD}" -s -i -H 'X-Requested-By: ambari' -X PUT -d \
    '{"HostRoles": {"state": "STARTED"}, "RequestInfo": {"context": "Start '"$TARGET"' via REST"}, "Body": {"ServiceInfo": {"state": "STARTED"}}}' \
    http://$AMBARI/api/v1/clusters/$CLUSTER/hosts/$TARGET/host_components/NODEMANAGER
}

turnoff () {
  curl -u "${AMBARI_USER}":"${AMBARI_PASSWD}" -s -i -H 'X-Requested-By: ambari' -X PUT -d \
    '{"HostRoles": {"state": "INSTALLED"}, "RequestInfo": {"context": "Stop '"$TARGET"' via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' \
    http://$AMBARI/api/v1/clusters/$CLUSTER/hosts/$TARGET/host_components/NODEMANAGER
}

request () {
  curl -u "${AMBARI_USER}":"${AMBARI_PASSWD}" -s -i -H 'X-Requested-By: ambari' "$1"
}

get_from_json_one () {
  filename=/tmp/extremelyunusualandlongfilename.py
  cat > $filename << EOF
import json
import sys
object = json.load(sys.stdin)
try:
    print(object["$1"])
except KeyError:
    pass
EOF
  python $filename
  rm $filename
}

get_from_json_two () {
  filename=/tmp/extremelyunusualandlongfilename.py
  cat > $filename << EOF
import json
import sys
object = json.load(sys.stdin)
try:
    print(object["$1"]["$2"])
except KeyError:
    pass
EOF
  python $filename
  rm $filename
}

extract_json () {
  awk 'index($0, "{") { doPrint = 1 } doPrint { print }'
}


if [ $# -ne 2 ]; then
  echo "${usage_msg}" >&2
  exit 1
fi

case "x$OPERATION" in
  "xstop")
    output=$(turnoff)
  ;;
  "xstart")
    output=$(turnon)
  ;;
  *)
    echo "error: unrecognized input argument" >&2
    echo "${usage_msg}" >&2
    exit 1
  ;;
esac

unset flag
case $(echo "$output" | head -n 1 | awk '{ print $2 }') in
  200)
    flag=y
  ;;
  202)
    url=$(echo "$output" | extract_json | get_from_json_one href)
  ;;
  *)
    echo "error: something went wrong" >&2
    exit 1
  ;;
esac

while test -z ${flag:+set}; do
  sleep 2s
  state=$(request "$url" | extract_json | get_from_json_two Requests request_status)
  test "x$state" = "xCOMPLETED" && flag=y
done
