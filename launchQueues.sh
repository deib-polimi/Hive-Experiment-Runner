#!/bin/bash

## Copyright 2016 Eugenio Gianniti
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

applist="${SCRIPT_DIR}/scratch/apps.tmp"
rm -f "$applist"

if [ "x${USE_DSTAT}" = "xyes" ]; then
  echo 'Starting dstat start.sh'
  "${SCRIPT_DIR}/dstat/start.sh" "${SCRIPT_DIR}"
fi

while read line; do
  "${SCRIPT_DIR}/singleJob.sh" ${line} &
done < "${SCRIPT_DIR}/config/ssdata.conf"

if [ "x${USE_DSTAT}" = "xyes" ]; then
  echo 'Starting dstat stopncollect.sh'
  "${SCRIPT_DIR}/dstat/stopncollect.sh" "${SCRIPT_DIR}" "fetched/session/"
fi

while read appId; do
  yarn logs -applicationId "$appId" > fetched/session/"$appId".AMLOG.txt
done < "$applist"

rm -f "$applist"
