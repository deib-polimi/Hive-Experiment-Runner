#!/bin/bash

USERNAME=${1:?"single queue.sh: missing user name"}
QUEUE=${2:?"single queue.sh: missing queue"}
QUERYNAME=${3:?"single queue.sh: missing query name"}

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

. ${SCRIPT_DIR}/config/variables.sh

rm -f ${SCRIPT_DIR}/scratch/stopSession.tmp
rm -f ${SCRIPT_DIR}/scratch/${USERNAME}.${QUERYNAME}.${QUEUE}.txt
if [ ! -d fetched/session ]; then
  mkdir -p fetched/session
fi

while [ ! -f ${SCRIPT_DIR}/scratch/stopSession.tmp ]; do
  rm -f ${SCRIPT_DIR}/scratch/temp_${QUERYNAME}.tmp
  TST=$(date "+%T.%3N")
  sudo -u $USERNAME hive -i ${SCRIPT_DIR}/queries/${QUEUE}.sql \
    -f ${SCRIPT_DIR}/queries/${QUERYNAME}.${QUERYEXTENSION} \
    &> ${SCRIPT_DIR}/scratch/temp_${QUERYNAME}.tmp
  TND=$(date "+%T.%3N")
  while read -r line; do
    if [[ "$line" =~ .*(application_[0-9]+_[0-9]+).* ]]; then
      strresult=${BASH_REMATCH[1]}
      echo "${strresult}, ${TST}, ${TND}" >> \
        fetched/session/${USERNAME}.${QUERYNAME}.${QUEUE}.txt
      break
    fi
  done < ${SCRIPT_DIR}/scratch/temp_${QUERYNAME}.tmp
  python waitExp.py
done
