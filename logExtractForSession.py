import subprocess
import sys
import re
import os
import urllib2
import time
from datetime import datetime
try:
	import cPickle as pickle
except:
	import pickle
import plotHelper as ph

verbose=True
ganglia=False

ganglia_metrics = "UNSET"
ganglia_global_prefix = "UNSET"
ganglia_base_prefix = "UNSET"
ganglia_base_inter = "UNSET"
ganglia_base_suffix = "UNSET"
ganglia_interval = "UNSET"
log_path="UNSET"
queues_target_url_prefix = "UNSET"
queues_target_url_suffix = "UNSET"
queue_list = "UNSET"

####################################
# Set variables from config/ files #
####################################
for line in open("config/python.conf","r").read().splitlines():
	sline = line.rstrip().split(" ")
	if "ganglia_interval" in sline[1]:
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

for line in open("config/variables.sh","r").read().splitlines():
	if line[0]!="#":
		sline = line.rstrip().split("=")
		if "LOG_PATH" in sline[0]:
			log_path = sline[1]
		elif "MASTER" in sline[0]:
			master = sline[1].strip("\"")

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

path = sys.argv[3]

hosts = open(os.path.join(sys.path[0], "config/hosts.txt"),"r").read().splitlines()

start_str = r'.+Storing application with id (application_[0-9]+_[0-9]+)'
print "Fetching application RM log for all sessions"
end_str = "capacity.ParentQueue .+ Application removed . appId: (application_[0-9]+_[0-9]+)"
fout = open(os.path.join(sys.path[0], path+"RMLOG.txt"),"w")
# Generate list of app run in the sessions, so we don't need to do it manually between step 1 and 2
fout_session = open(os.path.join(sys.path[0], path+"sessionList.txt"),"w")
fout_startEnd = open(os.path.join(sys.path[0], path+"appsStartEnd.bin"),"w")
#p = subprocess.Popen(['ssh', master, '\'cat '+log_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#p = subprocess.Popen(['cat', log_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#out=p.stdout.readlines()
out = open("/tmp/log.txt","r").readlines()

###############
# Fetch RMLOG #
###############
dt_start=-1
dt_end=-1
begun=False
after_first_finish=False
buffer = ""
count=0
time_string = r'([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+):([0-9]+):([0-9]+),([0-9]+).+'
time_string_ganglia = r'([0-9]+)-([0-9]+)-([0-9]+)T([0-9]+):([0-9]+):([0-9]+).+'
started_apps = {}

for line in out:
	count+=1
	if count%50000==0:
		print str(count/50000)+"x50 K"
	
	##########################################################################
	# Look for apps start time (earliest)  and end time (latest), while saving the log in between #
	##########################################################################
	found = re.search(start_str, line)
	if found:
		app = found.group(1)
		fout_session.write(app+"\n")
		found = re.search(time_string, line)
		this_time = dateTime(found)
		started_apps[app] = (this_time,-1)
		if not begun:
			begun = True
			dt_start = this_time
		
	# Look for apps end time
	# Once the first end is found, every other line will be put in a buffer, 
	# written on file and emptied every time we find another app end
	found = re.search(end_str, line)
	if found:
		app = found.group(1)
		found = re.search(time_string, line)
		this_time = dateTime(found)
		if app not in started_apps:
			print "Found end but not start for app "+app
			exit(-2)
		started_apps[app] = (started_apps[app][0],this_time)
		after_first_finish = True
		dt_end = this_time
		# Write the buffer and empty it
		buffer += line+"\n"
		fout.write(buffer)
		buffer = ""
		continue
	
	if after_first_finish:
		# Lines between two ends, or last end and bottom of the log
		buffer += line+"\n"
	elif begun:
		# Lines between first start and first end
		fout.write(line+"\n")
		
# Final check: do all start times have an end time?
for app in started_apps:
	if started_apps[app][1] == -1:
		print "ERROR - Probably the log was not flushed, end of log not found for "+app
		exit(-1)

fout_startEnd.write(pickle.dumps(started_app))

fout_startEnd.flush()
fout_startEnd.close()
fout.flush()
fout.close()
fout_session.flush()
fout_session.close()

##############################
# Fetch queues stats from Ganglia #
#############################
print "Fetching queues info from Ganglia"
for queue in queue_list:
	ganglia_out=open(os.path.join(sys.path[0], path+"/queue-"+queue+"-stats.csv"),"w")
	raw_csv = urllib2.urlopen(queues_target_url_prefix+queue+queues_target_url_suffix).read()
	if verbose and len(sraw_csv) < 100:
		print "Could not fetch something, looks like the file is empty:\n"+queues_target_url_prefix+queue+queues_target_url_suffix

# Save all the file, we take a slice only later, so if there is any mistake we still have the full log to use
	ganglia_out.write(raw_csv)
	ganglia_out.flush()
	ganglia_out.close()

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





