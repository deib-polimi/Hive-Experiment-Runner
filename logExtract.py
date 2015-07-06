import subprocess
import sys
import os
import urllib2
import time
import plotHelper as ph
import regularExpressions as myre
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

####################################
# Set variables from config/ files #
####################################
for line in open(os.path.join(sys.path[0], "config/python.conf"),"r").read().splitlines():
  sline = line.strip().split(" ")
  if "ganglia_interval" in sline[0]:
    ganglia_interval = int(sline[1])
  elif "ganglia_base_prefix" in sline[0]:
    ganglia_base_prefix = sline[1]
  elif "ganglia_global_prefix" in sline[0]:
    ganglia_global_prefix = sline[1]
  elif "ganglia_base_inter" in sline[0]:
    ganglia_base_inter = sline[1]
  elif "ganglia_base_suffix" in sline[0]:
    ganglia_base_suffix = sline[1]
  elif "ganglia_metrics" in sline[0]:
    ganglia_metrics = sline[1:]
  elif "fetch_ganglia_metrics" in sline[0]:
    if "true" in sline[1]:
      ganglia = True

for line in open(os.path.join(sys.path[0], "config/variables.sh"),"r").read().splitlines():
  if line and line[0] != "#":
    sline = line.rstrip().split("=")
    if "LOG_PATH" in sline[0]:
      log_path = sline[1]
    elif "MASTER" in sline[0]:
      master = sline[1].strip("\"")

app = sys.argv[1]
path = sys.argv[2]

hosts = open(os.path.join(sys.path[0], "config/hosts.txt"),"r").read().splitlines()
print str(len(hosts)) + " hosts loaded from config/hosts.txt"

##################################
# Fetch RM log with tail command #
##################################
print "Fetching application RM log for {}".format (app)
fout = open(path+app+".RMLOG.txt","w")
se = open(path+"appDuration.txt","a")
started_apps = {}

if os.path.isfile(path+"appsStartEnd.bin"):
  temp = open(path+"appsStartEnd.bin","r")
  try:
    started_apps=pickle.loads(temp.read())
  except EOFError:
    started_apps = {}
    print "WARNING: empty appsStartEnd.bin"
  print "Appending to bin app start-end list"
  temp.close()

fout_startEnd = open(path+"appsStartEnd.bin","w")

out=open("/tmp/log.txt","r").readlines()

###############################################################
# Parse RM log looking for slice belonging to the current app #
###############################################################
start=-1
end=-1
begun=False
finished=False
count=0
app_re = myre.App (app)

for line in out:
  count+=1
  if count%50000==0:
    print str(count/50000)+"x50 K"
  
  if not begun:
    found = app_re.start.search (line)
    if found:
      found = myre.Time.time.search (line)
      #print line
      print "begin!"
      begun=True
      fout.write(line)
      dt_start = myre.Time.dateTime (found)
      started_apps[app] = (dt_start,-1)
      start = myre.Time.getTime (found)
  elif not finished:
    found = app_re.end.search (line)
    if found:
      found = myre.Time.time.search (line)
      print "end!"
      finished=True 
      #print finished
      dt_end = myre.Time.dateTime (found)
      started_apps[app] = (started_apps[app][0],dt_end)
      end = myre.Time.getTime (found)
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
      ganglia_out=open(path+"/"+app+"-"+metric+"-"+host.strip(".")[0]+".csv","w")
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
  global_ganglia_out=open(path+"/"+app+"-"+metric+"-global.csv","w")
  target_url = ganglia_global_prefix + metric + ganglia_base_suffix
  print "Fetching " +metric
  print target_url
  raw_csv = urllib2.urlopen(target_url).read()
  print "Done, get slice"
  global_ganglia_out.write(ph.getSlice(raw_csv, dt_start, dt_end, 'ganglia'))
  global_ganglia_out.flush()
  global_ganglia_out.close()
