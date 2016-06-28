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

import plotHelper as ph
import sys
import os

path = sys.argv[1]

hosts = open(os.path.join(sys.path[0], 'config', 'hosts.txt'),'r').read().splitlines()

#############################
# Get the dstat file from each host #
#############################
list_csv = []
for host in hosts:
  print "Appending csv for {}".format(host)
  cur_dstat = open(os.path.join(path, 'stats.{host}.csv'.format(host=host)), 'r').read()
  list_csv.append(ph.cleanHeader(cur_dstat))

############################
# Make and write aggregated csv #
############################
fout = open(os.path.join(path, 'stats.global.csv'), 'w')
fout.write(ph.aggregateCsv(list_csv))
fout.flush()
fout.close()
