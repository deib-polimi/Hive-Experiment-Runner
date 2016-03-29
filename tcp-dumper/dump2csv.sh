#!/bin/bash
# tcpdump logs (readable-type) to csv

## Copyright 2016 Domenico Enrico Contino
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

# UTILITY
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

# SETUP
UPPER_DIR=$(dirname "${SCRIPT_DIR}")
PFX='dump.' # groups *.csv by prefix

i=0
while read host_name; do
  # Deletes numbers following the type of host and inserts the strings in an array
  str=$(echo $host_name | tr -d '[[:digit:]]')
  if [ $i -eq 0 ]; then # if it's first ride
    arrHosts[0]=$str
    let i=i+1
  else
    if [ $str != ${arrHosts[(($i-1))]} ]; then # if extracted item is different to last inserted
      arrHosts[$i]=$str
      let i=i+1
    fi
  fi
done < "${UPPER_DIR}/config/hosts.txt"

# Creates the repeated part of the regex for next step
for (( j=0; j<${#arrHosts[@]}; j++ )); do
  if [ $j -eq 0 ]; then
    rep='('
  fi
  # Writes the dynamic part of the regex
  rep="$rep${arrHosts[${j}]}"
  # Depending on counter, appends a specific symbol
  if [ $j -ne $(expr "${#arrHosts[@]}" - 1) ]; then
    rep="$rep|"
  else
    rep="$rep)"
  fi
done
# Repetita final form (example): (master|slave|datanode|namenode|computenode)([0-9]+)?.[0-9]+
rep="${rep}([0-9]+)?.[0-9]+"
regex="([0-9]+:[0-9]+:[0-9]+.[0-9]+)\ IP\ ${rep}\ >\ ${rep}:.*\ ([0-9]+)"

while read host_name; do
  for f in $(ls | grep "dump.${host_name}\.log"); do
    echo "On file: ${f}"
    header_in=0;
    header_out=0;
    # scrolling dump lines
    while read log_line; do
      # extract parameters to arrange lines into final .csv document
      if [[ $log_line =~ $regex ]]; then
        TIME="${BASH_REMATCH[1]}"
        SRC="${BASH_REMATCH[2]}${BASH_REMATCH[3]}"
        DST="${BASH_REMATCH[4]}${BASH_REMATCH[5]}"
        BYTES="${BASH_REMATCH[6]}"
        # if it's a OUT capture
        if [[ ! -z $(echo "${log_line}" | grep "${host_name}\..* >") ]]; then
          # writes the header
          if [ $header_out -eq 0 ]; then
            echo 'TIME,SRC,DST,BYTES' > "${PFX}${host_name}.OUT.csv" 2> /dev/null &
            header_out=1
          fi
          echo "${TIME},${SRC},${DST},${BYTES}" >> "${PFX}${host_name}.OUT.csv" 2> /dev/null &
        # or if it's a IN capture
        #else
        elif [[ ! -z $(echo "${log_line}" | grep "> ${host_name}\.") ]]; then
          if [ $header_in -eq 0 ]; then
            echo 'TIME,SRC,DST,BYTES' > "${PFX}${host_name}.IN.csv" 2> /dev/null &
            header_in=1
          fi  
          echo "${TIME},${SRC},${DST},${BYTES}" >> "${PFX}${host_name}.IN.csv" 2> /dev/null &
        fi
      fi
    done < "${f}" # while
  done #for
done < "${UPPER_DIR}/config/hosts.txt"

echo "$0: DONE"
