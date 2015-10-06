#!/usr/bin/env python2 -O

import csv
import glob
import os
import sys

gantts_dir = sys.argv[1]

for file_name in glob.glob (os.path.join (gantts_dir, "*")):
  if file_name.endswith (".csv"):
    if __debug__:
      print "Working on {}".format (file_name)
    tasks = list ()
    nodes = list ()
    starts = list ()
    ends = list ()
    phases = list ()
    containers = list ()
    with open (file_name, "rb") as infile:
      reader = csv.DictReader (infile)
      try:
        for row in reader:
          phases.append (row["Phase"])
          tasks.append (row["Task"])
          containers.append (row["Container"])
          nodes.append (row["Node"])
          starts.append (int (row["Start"]))
          ends.append (int (row["End"]))
      except KeyError:
        print "ERROR: csv file {} lacks required data".format (file_name)
        continue
    min_time = min (starts)
    starts[:] = [t - min_time for t in starts]
    ends[:] = [t - min_time for t in ends]
    out_file_name = file_name.replace (".csv", ".from0.csv")
    with open (out_file_name, "wb") as outfile:
      writer = csv.DictWriter (outfile,
                               fieldnames=["Phase", "Task", "Container",
                                           "Node", "Start", "End"])
      writer.writeheader ()
      for phase, task, node, start, end, container in zip (phases, tasks, nodes, starts, ends, containers):
        row = {"Phase" : phase, "Task" : task, "Node" : node,
               "Start" : start, "End" : end, "Container" : container}
        writer.writerow (row)
