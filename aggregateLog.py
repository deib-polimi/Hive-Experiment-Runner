import plotHelper as ph
import sys
import os

# >>>>> Fabio's way

# #################################################
# # Get the list of hosts, but exclude master as we don't care #
# #################################################
# master = "UNSET"
# for line in open("config/variables.sh","r").read().splitlines():
# 	if line and line[0] != "#":
# 		sline = line.split("=")
# 		if "MASTER" in sline[0]:
# 				master = sline[1].strip("\"")
# 				break
# 
# path = sys.argv[1]
# 
# hosts = open(os.path.join(sys.path[0], 'config/hosts.txt'),'r').read().splitlines()
# hosts.remove(master)

# =======

path = sys.argv[1]

hosts = open(os.path.join(sys.path[0], 'config/hosts.txt'),'r').read().splitlines()

# <<<<< My way (or the highway)

#############################
# Get the dstat file from each host #
#############################
list_csv = []
for host in hosts:
	print "Appending csv for "+host
	cur_dstat = open(path+'stats.'+host+'.csv','r').read()
	list_csv.append(ph.cleanHeader(cur_dstat))

############################
# Make and write aggregated csv #
############################
fout = open(path+'stats.global.csv','w')
fout.write(ph.aggregateCsv(list_csv))
fout.flush()
fout.close()
