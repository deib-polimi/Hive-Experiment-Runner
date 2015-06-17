#!/bin/sh

if [ $# -lt 1 ]; then
  echo "setup.sh: too few input arguments" 1>&2
  exit 1
fi

isnumber() { test "$1" && printf '%d' "$1" > /dev/null 2>&1; }

if [ ! isnumber $1 ]; then
  echo "setup.sh: an integer is needed as SCALE" >&2
  exit 2
fi
SCALE=$(printf '%d' "$1")

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

"${DIR}/directories.sh"
"${DIR}/tarballs.sh"
"${DIR}/dataset.sh" "${SCALE}" /tmp/ubuntu
