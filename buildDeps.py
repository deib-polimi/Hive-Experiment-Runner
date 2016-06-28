## Copyright 2015 Fabio Colzada
## Copyright 2016 Eugenio Gianniti
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

# This will write on file the dependencies of the vertices (serialized)
# It will run just once for the given query, since every run would be the same
# Args: file with hive explain output, path to destination file
import json
import os
import re
import sys

query = str(sys.argv[1])
path = str(sys.argv[2])
dependencies = {}

starting_dependency_listing = re.compile (r'Vertex dependency')
new_dependency = re.compile (r'(.+[0-9]+) \(.+\)')

# Obtain dag structure by querying hive, build dependencies among vertices and prepare other vertex structures
print("Get DAG structure from HIVE output...")

with open (query, "r") as infile:
  deps_found = False
  for line in infile:
    if not deps_found:
      found = starting_dependency_listing.search (line)
      if found:
        deps_found = True
    else:
      line = line.strip()
      if "<-" not in line:
        break
      sline = line.split("<-")
      vx = sline[0].strip()
      dependencies[vx]=[]
      deps = sline[1].split(",")
      for dep in deps:
        found = new_dependency.search (dep)
        if found:
          dep = found.group (1)
        else:
          print "Unexpected vertex name: {dep}".format (dep=dep)
          sys.exit (-1)
        dependencies[vx].append(dep.strip())
  if not deps_found:
    print "Could not catch begin of DAG description, aborting."
    sys.exit (-1)

with open (path, "w") as outfile:
  outfile.write (json.dumps (dependencies))

print "List of dependencies: "
print dependencies
