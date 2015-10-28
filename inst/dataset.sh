#!/bin/sh

if [ $# -lt 2 ]; then
  echo "dataset.sh: too few input arguments" 1>&2
  exit 1
fi

isnumber() { test "$1" && printf '%d' "$1" > /dev/null 2>&1; }

if [ ! isnumber $1 ]; then
  echo "dataset.sh: an integer is needed as SCALE" >&2
  exit 2
fi
SCALE=$(printf '%d' "$1")

SCRATCH_DIR="$2"

INITIAL_DIR=$(pwd)

cd "${HOME}"
git clone https://github.com/hortonworks/hive-testbench.git
cd hive-testbench/tpcds-gen
wget home.deib.polimi.it/arizzi/tpcds_kit.zip
cd ..
sudo apt-get -y install gcc make maven2
./tpcds-build.sh
./tpcds-setup.sh "${SCALE}" "${SCRATCH_DIR}"

cd "${INITIAL_DIR}"
