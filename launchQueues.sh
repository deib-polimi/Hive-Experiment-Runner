#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

while read line; do
  echo "$(date +%T): Launching ${line}"
  "${SCRIPT_DIR}/singleQueue.sh" ${line} &
done < ${SCRIPT_DIR}/config/ssdata.conf
