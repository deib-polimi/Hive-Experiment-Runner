# script-fabio
This `git` repository contains the dreaded scripts written by Fabio to
launch Hive queries and collect their logs.

## Take a Look Around

* `config/` stores the configuration files;
* `scratch/` hosts temporary files created by the scripts;
* `queries/` stores data about queries;
* `inst/` hosts scripts to ease installation on Instacluster;
* `gantt/` holds scripts to read task durations from aggregated log data and produce
           Gantt charts.

## Getting Started

To start using these scripts, edit the configuration files, providing the
URL to Ganglia (up to ganglia/) in `config/python.conf`, correctly setting
log file path and master node in `config/variables.sh`, and providing a
list of all the nodes in the cluster in `config/hosts.txt`.
Further, one should install dstat on all nodes, for instance running
`ansible` on the master, and run the `setup.sh` script from `inst/`.
Its only input is the dataset size in GB, not less than 2.

## Launching Queries

There are two main ways to use these scripts: either profiling queries on a dedicated
cluster, or running multi-user sessions.

* `runAndFetchSingle.sh` allows to profile queries on a dedicated cluster according
to the configuration set in `config/variables.sh`;
* `launchQueues.sh` repeatedly launches the concurrent queries stated in
    `config/ssdata.conf` until `scratch/stopSession` is created.
