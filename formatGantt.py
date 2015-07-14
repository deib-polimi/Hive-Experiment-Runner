import sys
import os
import csv
import glob

query_list = []
for line in open (os.path.join(sys.path[0], "config/variables.sh"), "r").read ().splitlines ():
  if line and line[0] != "#":
    sline = line.split ("=")
    if "QUERIES" in sline[0]:
      query_list = sline[1].strip ("\"").split (" ")
      print "Working on the following queries: " + str (query_list)
      break

for query in query_list:
  gantts_dir = os.path.join ("fetched", query, "gantts")
  if not os.path.exists (gantts_dir):
    print "ERROR: missing gantts directory for {}".format (query)
    continue
  
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
