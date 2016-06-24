#!/bin/bash

## Copyright 2015-2016 Alessandro Maria Rizzi, Eugenio Gianniti
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

USERNAME=${1:?"singleJob.sh: missing user name"}
QUEUE=${2:?"singleJob.sh: missing queue"}
QUERYNAME=${3:?"singleJob.sh: missing query name"}

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

. "${SCRIPT_DIR}/config/variables.sh"

STOP_FLAG="${SCRIPT_DIR}/scratch/stopSession"
TIME_FORMAT="+%d %T.%3N"

rm -f "${STOP_FLAG}"
if [ ! -d fetched/session ]; then
  mkdir -p fetched/session
fi

out=$(mktemp --tmpdir=fetched/session/ -q "${USERNAME}_${QUERYNAME}_${QUEUE}_XXXXX.csv")

while [ ! -f "${STOP_FLAG}" ]; do
  sql=$(mktemp --tmpdir="${SCRIPT_DIR}/scratch/" -q "${USERNAME}_${QUEUE}_${QUERYNAME}.XXXXX.sql")
  tmp=$(mktemp --tmpdir="${SCRIPT_DIR}/scratch/" -q "${USERNAME}_${QUEUE}_${QUERYNAME}.XXXXX.tmp")

  sed -e "s#DB_NAME#${DB_NAME}#g" "${SCRIPT_DIR}/queries/my_init.sql" > "${sql}"
  echo "set tez.queue.name=${QUEUE};" >> "${sql}"

  echo "$(date): Launching ${USERNAME} ${QUERYNAME} ${QUEUE}"
  TST=$(date "${TIME_FORMAT}")
  sudo -u "$USERNAME" hive -i "${sql}" \
    -f "${SCRIPT_DIR}/queries/${QUERYNAME}.${QUERYEXTENSION}" > "${tmp}" 2>&1
  TND=$(date "${TIME_FORMAT}")
  while read -r line; do
    if [[ "$line" =~ .*(application_[0-9]+_[0-9]+).* ]]; then
      strresult=${BASH_REMATCH[1]}
      echo "${strresult},${TST},${TND}" >> "${out}"
      echo "$strresult" >> "${SCRIPT_DIR}/scratch/apps.tmp"
      break
    fi
  done < "${tmp}"

  [ "x${DEBUG}" = "xyes" ] || rm "${sql}" "${tmp}"

  python "${SCRIPT_DIR}/waitExp.py"
done
