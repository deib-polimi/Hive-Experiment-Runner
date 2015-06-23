# This will write on file the dependencies of the vertexes (serialized)
# It will run just once for the given query, since every run would be the same
# Args: file with hive explain output, path to destination file
try:
  import cPickle as pickle
except:
  import pickle
import re
import sys
import os

query = str(sys.argv[1])
path = str(sys.argv[2])
dependencies = {}
fout=open(os.path.join(sys.path[0], path),"w")

# Obtain dag structure by querying hive, build dependencies among vertexes and prepare other vertex structures
print("Get DAG structure from HIVE output...")

out = open(query,"r").readlines()
skip = True
for line in out:
  if skip==True:
    found = re.search(r'.*Edges:', line)
    if found:
      skip=False
      continue
  if skip==False:
    line = line.strip()
    #print line
    if "<-" not in line:
      break
    sline = line.split("<-")
    #print sline
    vx = sline[0].strip()
    dependencies[vx]=[]
    deps = sline[1].split(",")
    #print deps
    for dep in deps:
      found = re.search(r'(.+[0-9]+) \(.+\)',dep)
      if found:
        dep = found.group(1)
        #print dep
      else:
        print("Unexpected vertex name: ")+dep
        exit(-1)
      dependencies[vx].append(dep.strip())
  #print line
if skip==True:
  print("Could not catch begin of dag description, aborting.")
  exit(-1)


fout.write(pickle.dumps(dependencies))
fout.flush()
fout.close()

print("List of dependencies: ")
print(dependencies)
