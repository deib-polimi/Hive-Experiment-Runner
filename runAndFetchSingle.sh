#!/bin/bash
# run specified query many times and fetch log and stats in an appropriate folder
# A file with all the hosts, line by line, is expected in the same folder

## Copyright 2015 Fabio Colzada, Eugenio Gianniti
## Copyright 2016 Eugenio Gianniti, Domenico Enrico Contino
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

# SETUP
. "${SCRIPT_DIR}/config/variables.sh"
CURHOST=$(hostname)

for QUERYNAME in ${QUERIES}; do
  # INIT
  EXTERNALCOUNTER=1

  rm -r -f fetched/$QUERYNAME
  mkdir -p fetched/$QUERYNAME
  # Renewed here and at every external loop, the incremental list is in the queries output folder
  rm -f "${SCRIPT_DIR}/scratch/apps.tmp"

  ####################################
  # Calls tcp-dumper start.sh script #
  ####################################
  if [ "x${USE_TCPDUMP}" = "xyes" ]; then
    echo 'Starting tcp-dumper start.sh'
    "${SCRIPT_DIR}/tcp-dumper/start.sh" "${SCRIPT_DIR}" "fetched/$QUERYNAME"
  fi

  if [ "x${USE_DSTAT}" = "xyes" ]; then
    echo 'Starting dstat start.sh'
    "${SCRIPT_DIR}/dstat/start.sh" "${SCRIPT_DIR}"
  fi

  while [ $EXTERNALCOUNTER -le $EXTERNALITER ]; do
    COUNTER=1
    echo "Running external iteration: $EXTERNALCOUNTER"

    #####################################################
    # Get query explain from hive to build dependencies #
    #####################################################
    init_file="${SCRIPT_DIR}/scratch/init.sql"
    if [ ! -f fetched/$QUERYNAME/dependencies.bin ]; then
      q=$(cat "${SCRIPT_DIR}/queries/${QUERYNAME}.${QUERYEXTENSION}")
      explain_query="explain ${q}"
      echo "$explain_query" > "${SCRIPT_DIR}/scratch/deleteme.tmp"
      echo "Get query explain from hive..."
      sed "s/DB_NAME/${DB_NAME}/g" "${SCRIPT_DIR}/queries/my_init.sql" \
        > "${init_file}"
      explain=$(hive -i "${init_file}" -f "${SCRIPT_DIR}/scratch/deleteme.tmp")
      echo "${explain}" > "${SCRIPT_DIR}/scratch/deleteme.tmp"
      python "${SCRIPT_DIR}/buildDeps.py" "${SCRIPT_DIR}/scratch/deleteme.tmp" fetched/$QUERYNAME/dependencies.bin
      echo "Dependencies loaded in fetched/$QUERYNAME/dependencies.bin"
      rm "${SCRIPT_DIR}/scratch/deleteme.tmp"
    else
      echo "Dependencies file already there, skipping..."
    fi

    #################################################################################################################
    # Run n times our query, save the application id in scratch/apps.tmp and fetched/$QUERYNAME/apps_$QUERYNAME.txt #
    #################################################################################################################
    tmp_file="${SCRIPT_DIR}/scratch/temp.tmp"
    while [ $COUNTER -le $INTERNALITER ]; do
      echo "Running query. Attempt $COUNTER"
      TST=$(date +"%T.%3N")
      hive -i "${init_file}" \
        -f "${SCRIPT_DIR}/queries/${QUERYNAME}.${QUERYEXTENSION}" \
        > "${tmp_file}" 2>&1
      TND=$(date +"%T.%3N")

      #################################################
      # Save app name in permanent and temporary file #
      #################################################
      while read -r line; do
        if [[ $line =~ .*(application_[0-9]+_[0-9]+).* ]]; then
          strresult=${BASH_REMATCH[1]}
          echo "Finished app: $strresult"
          echo "$strresult" >> fetched/$QUERYNAME/apps_$QUERYNAME.txt
          echo "$strresult" >> "${SCRIPT_DIR}/scratch/apps.tmp"
          echo -e "${strresult}\t${TST}\t${TND}">> fetched/$QUERYNAME/real_start_end.txt
          break
        fi
      done < "${tmp_file}"
      rm -f "${tmp_file}"

      COUNTER=$(( $COUNTER + 1 ))
    done

    #########################################################################
    # Wait some secs for flushing of previous logs, 2 mins should be enough #
    #########################################################################
    echo "Waiting 120s for logs to be flushed."
    sleep 120s
    rm -f /tmp/log.txt
    ##########################################################################
    # For each app, fetch the logs and run the python script to get the time #
    # intervals for our analysis                                             #
    ##########################################################################
    while read appname; do
      echo "Going to fetch AM logs for $appname"
      yarn logs -applicationId $appname > fetched/$QUERYNAME/${appname}.AMLOG.txt
      echo "Going to fetch RM logs for $appname"
      CATTEMPT=1
      if [ ! -f /tmp/log.txt ]; then
        if [ "x$CURHOST" = "x$MASTER" ]; then
          echo "Fetching RM log from local (we are on master)"
          tail ${LOG_PATH} -c 20MB > /tmp/log.txt
        else
          echo "Fetching RM log from master"
          < /dev/null ssh $MASTER "tail ${LOG_PATH} -c 20MB > /tmp/log.txt"
          < /dev/null scp ${MASTER}:/tmp/log.txt /tmp/log.txt
        fi
      else
        echo "RM already fetched. Moving on..."
      fi
      python "${SCRIPT_DIR}/logExtract.py" $appname fetched/$QUERYNAME/
      PRESULT=$?
      while [ $PRESULT -eq 255 ] && [ $CATTEMPT -le $FETCH_ATTEMPTS ]; do
        sleep 10s
        fetch_command="cat ${LOG_PATH}.1 ${LOG_PATH} | tail -c 20MB > /tmp/log.txt"
        if [ "x$CURHOST" = "x$MASTER" ]; then
          echo "Fetching RM log from local (we are on master)"
          eval ${fetch_command}
        else
          echo "Fetching RM log from master"
          < /dev/null ssh $MASTER "${fetch_command}"
          < /dev/null scp ${MASTER}:/tmp/log.txt /tmp/log.txt
        fi
        echo "Trying to fetch log again because end of RM log was not found... Attempt $CATTEMPT"
        python "${SCRIPT_DIR}/logExtract.py" $appname fetched/$QUERYNAME/
        PRESULT=$?
        CATTEMPT=$(( $CATTEMPT + 1 ))
      done

    done < "${SCRIPT_DIR}/scratch/apps.tmp"

    rm -f /tmp/log.txt
    rm "${SCRIPT_DIR}/scratch/apps.tmp"

    EXTERNALCOUNTER=$(( $EXTERNALCOUNTER + 1 ))
  done

  rm -f "${init_file}"

  if [ "x${USE_TCPDUMP}" = "xyes" ]; then
    echo 'Starting tcp-dumper stopncollect.sh'
    "$SCRIPT_DIR/tcp-dumper/stopncollect.sh" "${SCRIPT_DIR}" "fetched/$QUERYNAME"
  fi

  if [ "x${USE_DSTAT}" = "xyes" ]; then
    echo 'Starting dstat stopncollect.sh'
    "${SCRIPT_DIR}/dstat/stopncollect.sh" "${SCRIPT_DIR}" "fetched/$QUERYNAME"
  fi

done
