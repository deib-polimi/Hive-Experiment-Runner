#!/bin/bash
# Start/Stop ComputeNodes via Ambari

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

. "${SCRIPT_DIR}/config/variables.sh"
TARGET="$1"


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


usage_msg="usage: $0 [target] [stop|start]"

if [ $# -ne 2 ]; then
  echo "${usage_msg}" >&2
  exit 1
fi

case "x$2" in
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
