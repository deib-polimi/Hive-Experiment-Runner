import subprocess
import sys
import re
import os
import urllib2
import time
import plotHelper as ph
from datetime import datetime
try:
	import cPickle as pickle
except:
	import pickle

verbose=True
ganglia=False

ganglia_metrics = "UNSET"
ganglia_base_prefix = "UNSET"
ganglia_global_prefix = "UNSET"
ganglia_base_inter = "UNSET"
ganglia_base_suffix = "UNSET"
ganglia_interval = "UNSET"
log_path="UNSET"
master="UNSET"

def getTime(some):
	h = int(some.group(4))*60*60*1000
	m = int(some.group(5))*60*1000
	s = int(some.group(6))*1000
	ms = int(some.group(7))
	return (h+m+s+ms)

def dateTime(some):
	y = int(some.group(1))
	m = int(some.group(2))
	d = int(some.group(3))
	h = int(some.group(4))
	mm = int(some.group(5))
	s = int(some.group(6))
	return datetime(y,m,d,h,mm,s)

###############################
# Set variables from config/variables.sh file #
###############################
for line in open("config/variables.sh","r").read().splitlines():
	if line[0:2]=="#%":
		sline = line.rstrip().split(" ")
		if "log_path" in sline[1]:
			log_path = sline[2]
		elif "ganglia_interval" in sline[1]:
			ganglia_interval = int(sline[2])
		elif "ganglia_base_prefix" in sline[1]:
			ganglia_base_prefix = sline[2]
		elif "ganglia_global_prefix" in sline[1]:
                        ganglia_global_prefix = sline[2]
		elif "ganglia_base_inter" in sline[1]:
			ganglia_base_inter = sline[2]
		elif "ganglia_base_suffix" in sline[1]:
			ganglia_base_suffix = sline[2]
		elif "ganglia_metrics" in sline[1]:
			ganglia_metrics = sline[2:]
		elif "fetch_ganglia_metrics" in sline[1]:
			if "true" in sline[2]:
				ganglia = True
	elif 'MASTER' in line[0:10]:
		sline = line.rstrip().split("=")
		master=sline[1].strip("\"")

app = sys.argv[1]
path = sys.argv[2]

hosts = open(os.path.join(sys.path[0], "config/hosts.txt"),"r").read().splitlines()
print str(len(hosts)) + " hosts loaded from config/hosts.txt"

#############################
# Fetch RM log with tail command #
#############################
start_str = "Storing application with id "+app
print "Fetching application RM log for "+app
end_str = "capacity.ParentQueue .+ Application removed.+appId: "+app
fout = open(os.path.join(sys.path[0], path+app+".RMLOG.txt"),"w")
se = open(os.path.join(sys.path[0], path+"appDuration.txt"),"a")
#command = 'ssh '+master+' \'tail '+log_path+' -c 20MB\''
#print command
#p = subprocess.Popen(['tail', "/tmp/log.txt", "-c 20MB"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#p = subprocess.Popen(['tail', log_path, '-c 20MB'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
started_apps = {}

if os.path.isfile(os.path.join(sys.path[0], path+"appsStartEnd.bin")):
	temp = open(os.path.join(sys.path[0], path+"appsStartEnd.bin"),"r")
	started_apps=pickle.loads(temp.read())
	print "Appending to bin app start-end list"
	temp.close()

fout_startEnd = open(os.path.join(sys.path[0], path+"appsStartEnd.bin"),"w")

#out=p.stdout.readlines()
# readlines() maintains the \n
out=open("/tmp/log.txt","r").readlines()
#print out
##################################################
# Parse RM log looking for slice belonging to the current app #
##################################################
start=-1
end=-1
begun=False
finished=False
count=0
time_string = r'([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+):([0-9]+):([0-9]+),([0-9]+).+'
time_string_ganglia = r'([0-9]+)-([0-9]+)-([0-9]+)T([0-9]+):([0-9]+):([0-9]+).+'

for line in out:
	count+=1
	if count%50000==0:
		print str(count/50000)+"x50 K"
	
	if not begun:
		found = re.search( r'.*'+start_str+".*", line)
		if found:
			found = re.search(time_string, line)
			#print line
			print "begin!"
			begun=True
			fout.write(line)
			dt_start = dateTime(found)
			started_apps[app] = (dt_start,-1)
			start = getTime(found)
	elif not finished:
		found = re.search( r'.*'+end_str+".*", line)
		if found:
			found = re.search(time_string, line)
			print "end!"
			finished=True 
			#print finished
			dt_end = dateTime(found)
			started_apps[app] = (started_apps[app][0],dt_end)
			end = getTime(found)
			fout.write(line)
			break
		fout.write(line)

#print "Done "+str(finished)
fout.flush()
fout.close()

if not finished:
	print "ERROR - Probably the log was not flushed, end of log not found for "+app
	exit(-1)
else:
	print "Done extracting RM log for "+app
	se.write(str(end-start)+"\t"+app+"\n")

fout_startEnd.write(pickle.dumps(started_apps))
fout_startEnd.flush()
fout_startEnd.close()

####################################
# Fetching info from Ganglia for every host #
####################################
if ganglia==True:
	print "Fetching info from Ganglia"
	for host in hosts:
		for metric in ganglia_metrics:
			ganglia_out=open(os.path.join(sys.path[0], path+"/"+app+"-"+metric+"-"+host.strip(".")[0]+".csv"),"w")
			target_url = ganglia_base_prefix + host + ganglia_base_inter + metric + ganglia_base_suffix
			print "Fetching " +metric+" @ "+host
			raw_csv = urllib2.urlopen(target_url).read()
			ganglia_out.write(ph.getSlice(raw_csv, dt_start, dt_end, 'ganglia'))
			ganglia_out.flush()
			ganglia_out.close()

############################################
# In any case, use ganglia to fetch cluster wide stats #
############################################
print "Fetching cluster-wide info from Ganglia"
for metric in ganglia_metrics:
	global_ganglia_out=open(os.path.join(sys.path[0], path+"/"+app+"-"+metric+"-global.csv"),"w")
	target_url = ganglia_global_prefix + metric + ganglia_base_suffix
	print "Fetching " +metric
	print target_url
	raw_csv = urllib2.urlopen(target_url).read()
	print "Done, get slice"
	global_ganglia_out.write(ph.getSlice(raw_csv, dt_start, dt_end, 'ganglia'))
	global_ganglia_out.flush()
	global_ganglia_out.close()


