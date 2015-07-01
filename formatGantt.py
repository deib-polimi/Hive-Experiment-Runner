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

do_debug = (os.getenv ("DEBUG", "no") == "yes")

for query in query_list:
  gantts_dir = os.path.join ("fetched", query, "gantts")
  if not os.path.exists (gantts_dir):
    print "ERROR: missing gantts directory for {}".format (query)
    continue
  
  for file_name in glob.glob (os.path.join (gantts_dir, "*")):
    if file_name.endswith (".csv"):
      if do_debug:
        print "Working on {}".format (file_name)
      with open (file_name, "rb") as infile:
        with open (file_name.replace (".csv", ".tsv"), "wb") as outfile:
          reader = csv.DictReader (infile)
          field_names = reader.fieldnames
          writer = csv.writer (outfile, delimiter="\t")
          if "Task" in field_names and "Node" in field_names and "Start" in field_names and "End" in field_names:
            for inrow in reader:
              outrow = [inrow["Node"], inrow["Start"], inrow["End"], inrow["Task"]]
              writer.writerow (outrow)
          else:
            print "ERROR: csv file lacks required data"
