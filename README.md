This repository contains the dreaded scripts written by Fabio to
launch Hive queries and parse their logs.

# A Little Bit of Instructions
`config/` stores the configuration files.

`scratch/` hosts temporary files created by the scripts.

`queries/` stores data about queries.

`inst/` hosts scripts to ease installation on Instacluster.

To start using these scripts, edit the configuration files, providing the
URL to Ganglia (up to ganglia/) in `python.conf` and correctly setting
log file path and master node in `variables.sh`.
Further, one should install dstat on all nodes, for instance running
`ansible` on the master, and run the `setup.sh` script from `inst/`.
