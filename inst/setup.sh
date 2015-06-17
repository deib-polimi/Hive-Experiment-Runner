#!/bin/sh

if [ $# -lt 1 ]; then
  echo "setup.sh: too few input arguments" 1>&2
  exit 1
fi

isnumber() { test "$1" && printf '%d' "$1" > /dev/null 2>&1; }

isnumber "$1" || ( echo "setup.sh: an integer is needed as SCALE" >&2; exit 2 )
SCALE=$(printf '%d' "$1")

SOURCE="$0"
while [ -L "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [ $SOURCE != /* ] && SOURCE="$DIR/$SOURCE"
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

"${DIR}/directories.sh"
"${DIR}/tarballs.sh"
"${DIR}/dataset.sh" "${SCALE}" /tmp/ubuntu
