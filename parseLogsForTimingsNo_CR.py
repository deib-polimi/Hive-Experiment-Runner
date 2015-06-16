# For every query present in the list, for every app run for using that query, parse the logs
# in the appropriate folder, collecting info about main time intervals and writing on several 
# files, common to the apps of a same query, info for the subsequent dag creation 
import sys
import os
import re
import shutil
from datetime import datetime
try:
	import cPickle as pickle
except:
	import pickle

time_string_RM = r'([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+):([0-9]+):([0-9]+),([0-9]+).+'

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
	return datetime.datetime(y,m,d,h,mm,s)

##############################
# Populate list of queries to analyze #
##############################
query_list = []
for line in open("variables.sh","r").read().splitlines():
	sline = line.split("=")
	if "QUERIES" in sline[0]:
		query_list = sline[1].strip("\"").split(" ")
		print "Working on the following queries: "+str(query_list)
		break

#########################################################
# Outer iteration, for every query, clean/make the query results folder #
#########################################################
for query in query_list:
	working_dir = os.path.join(sys.path[0], "fetched/"+query)
	final_result_dir = os.path.join(sys.path[0], "fetched/"+query+"/results")
	if os.path.exists(final_result_dir):
		shutil.rmtree(final_result_dir)
	os.makedirs(final_result_dir)

	#################
	# Open output files #
	#################
	fc = open(final_result_dir+"/firstContainerInfo.txt","a")
	rc = open(final_result_dir+"/releaseContainer.txt","a")
	gc = open(final_result_dir+"/genericContainerStartup.txt","a")
	ca = open(final_result_dir+"/containerAcquisition.txt","a")
	#DAG specific output files
	al = open(final_result_dir+"/appsList.txt","a")
	vo = open(final_result_dir+"/vertexOrder.txt","a")
	vltk = open(final_result_dir+"/vertexLtask.txt","a")
	vpri = open(final_result_dir+"/vertexPriority.txt","a")
	otk = open(final_result_dir+"/taskLaunchOrder.txt","a")
	tdlo = open(final_result_dir+"/taskDurationLO.txt","a")

	#################################################
	# For every app run for the current query, collect all the info #
	#################################################
	app_list = open(working_dir+"/apps_"+query+".tmp","r").read().split("\n")
	for app in app_list:
		# Input files for the specific app
		rmLog = open(working_dir+"/"+app+".RMLOG.txt","r")
		amLog = open(working_dir+"/"+app+".AMLOG.txt","r")
		isOldMapping=False
		if os.path.isfile(final_result_dir+"/vmap.bin"):
			vmap = open(final_result_dir+"/vmap.bin","r")
			print "Found mapping vname-vid, using this."
			map_vid_vname=pickle.loads(vmap.read())
			isOldMapping=True
		else:
			vmap = open(final_result_dir+"/vmap.bin","w")
			print "First mapping vname-vid"
			map_vid_vname={}
			isOldMapping=False

		#########################
		# Parsing AM log, line by line #
		########################
		print "Parsing AM log"
		line = amLog.readline()
		# For containers that were running
		release_am_side={}
		# Type of released container: EXP for expired containers, NEW if new but unused, if not present, consider END (reach end of application life)
		container_type={} 
		first_container_startup_status="NULL"
		first_container_startup=(-1,-1)
		first_container_release=(-1,-1)
		first_container_epilogue=(-1,-1)
		generic_container_startup_status="NULL"
		generic_container_startup=[]
		container_acquisition={}
		current_container=""
		last_time = -1
		this_app="NULL"
		counter=0
		# DAG specific
		# List of vx as they are pre-processed by tez
		vertex_order=[]
		# Map a vertex to its task list
		map_vx_ltk={}
		# For every task attempt, the container it belongs to
		map_task_cnt={}
		# Vice versa
		map_cnt_task={}
		# Task attempts ordered as they are assigned to a container
		task_order=[]
		# Map a vertex to its priority
		map_vx_pri={}
		tk_start_end={}
		tk_start_end_fulltime={}
		TK_STATUS="NULL"
		last_task="NULL"
		end_DAG=False

		while line:
			counter+=1
			if counter%1000==0:
				print str(counter/1000)+"K"

			# Case: non-blocking check over container type, case expired
			found = re.search(r".*No taskRequests. Container\'s idle timeout delay expired or is new. Releasing container, .*(container_[0-9]+_[0-9]+_[0-9]+_[0-9]+).*isNew=false", line)
			if found:
				cnt = found.group(1)
				container_type[cnt]="EXP"
			# Case: non-blocking check to be at the end of dag execution
			found = re.search(r'.*app.DAGAppMaster: Calling stop for all the services', line)
			if found:
				end_DAG=True
			# Case: release container request, AM side.
			# This is sent also for expired containers, not just deallocating container on dag exit.
			found = re.search(r'.*Sending a stop request to the NM for ContainerId: (container_[0-9]+_[0-9]+_[0-9]+_[0-9]+).*', line)
			if found:
				cnt = found.group(1)
				#print "Stopping "+cnt
				if not end_DAG:
					print "Sending container stop request before end of dag (expired): "+cnt
				#	exit(-1)
				if cnt in release_am_side.keys():
					print "Container released after release? "+cnt
				found = re.search(time_string_RM,line)
				release_am_side[cnt] = getTime(found)
				line = amLog.readline()
				continue
			# Case: release container because new container and no task, AM side
			found = re.search(r".+rm.YarnTaskSchedulerService: Releasing unused container: (container_[0-9]+_[0-9]+_[0-9]+_[0-9]+)", line)
			if found:
				cnt = found.group(1)
				if cnt in release_am_side.keys():
					print "Container released after release? "+cnt
				found = re.search(time_string_RM, line)
				this_time = getTime(found)
				release_am_side[cnt] = this_time
				if cnt in container_acquisition.keys():
					print "Double container_acquisition for "+cnt
					exit(-1)
				container_acquisition[cnt]=(-1,this_time,-1,"NEW")
				container_type[cnt]="NEW"
				line = amLog.readline()
				continue
			# Container received, set element in container_acquisition
			found = re.search(r".*Assigning container to task, container=Container: \[ContainerId: (container_[0-9]+_[0-9]+_[0-9]+_[0-9]+).*", line)
			if found:
				cnt = found.group(1)
				found = re.search(time_string_RM, line)
				this_time = getTime(found)
				if cnt in container_acquisition.keys():
					quadruple = container_acquisition[cnt]
					received = quadruple[1]
					started = quadruple[2]
					ctype = quadruple[3]
					# Update value only if it's the first task to be assigned to this container, skip otherwise
					if received < 0:
						container_acquisition[cnt]=(-1,this_time,started,ctype)
				else:
					container_acquisition[cnt]=(-1,this_time,-1,"GEN")
				line = amLog.readline()
				continue
					
			# Case: startup/epilogue/release time for the am container
			#--------------------------------------------
			# Case: we just found the beginning of the am container log (header)
			if "NULL" in first_container_startup_status:
				found = re.match(r'Container: (container_[0-9]+_[0-9]+_[0-9]+_000001) on .*', line)
				if found:
					current_container=found.group(1)
					first_container_startup_status="INIT"
					line = amLog.readline()
					continue
			# Case: found the beginning of the first container activity (begin of startup)
			if "INIT" in first_container_startup_status:
				found = re.search(r'.+app.DAGAppMaster: Created DAGAppMaster for application appattempt.*', line)
				if found:
					found = re.search(time_string_RM, line)
					this_time = getTime(found)
					if current_container in container_acquisition.keys():
						print "Double container_acquisition for "+current_container
						exit(-1)
					else:
						container_acquisition[current_container]=(-1,-1,this_time,"1ST")
					current_container = ""
					first_container_startup_status="START"
					first_container_startup=(this_time,-1)
					line = amLog.readline()
					continue
			# Case: end of container startup, it starts generating new tasks
			if "START" in first_container_startup_status:
				found = re.search(r'.+impl.ImmediateStartVertexManager: Starting [0-9]+ in .+', line)
				if found:
					first_container_startup_status="MIDDLE"
					found = re.search(time_string_RM, line)
					first_container_startup=(first_container_startup[0],getTime(found))
					line = amLog.readline()
					continue
			# Case: look for the the end of the dag, epilogue begins
			if "MIDDLE" in first_container_startup_status:
				found = re.search(r'.+impl.DAGImpl: dag_[0-9]+_[0-9]+_[0-9]+ transitioned from RUNNING to SUCCEEDED', line)
				if found:
					first_container_startup_status="EPILOGUE"
					if last_time < 0:
						print "ERROR - Unexpected last_time value: "+str(last_time)
						exit(-1)
					first_container_epilogue=(last_time,-1)
					line = amLog.readline()
					continue
				else:
					found = re.search(time_string_RM, line)
					if found:
						last_time = getTime(found)
					# no continue here, this line could be in following checks
			# Case: last entry for first container log, end of epilogue, beginning of first container release
			if "EPILOGUE" in first_container_startup_status:
				found = re.search(r'.+app.DAGAppMaster: The shutdown handler has completed', line)
				if found:
					first_container_startup_status="END"
					found = re.search(time_string_RM, line)
					last_time = getTime(found)
					first_container_epilogue=(first_container_epilogue[0],last_time)
					first_container_release=(last_time,-1)
					line = amLog.readline()
					continue
			#--------------------------------------------
			
			# Case: generic container
			found = re.search(r'Container: (container_[0-9]+_[0-9]+_[0-9]+_[0-9]+).+', line)
			if found:
				current_container=found.group(1)
				line = amLog.readline()
				continue
			# Case: container just started
			found = re.search(r'.+INFO.+main.+task.TezChild: TezChild starting', line)
			if found:
				if "NULL" not in generic_container_startup_status:
					print "Unexpected status of first_container_startup_status: "+generic_container_startup_status
					exit(-1)
				generic_container_startup_status="BEGIN"
				found = re.search(time_string_RM, line)
				this_time = getTime(found)
				generic_container_startup.append((this_time,-1))
				if current_container in container_acquisition.keys():
					container_acquisition[current_container]=(-1,container_acquisition[current_container][1],this_time,"GEN")
				else:
					container_acquisition[current_container]=(-1,-1,this_time,"GEN")
				current_container=""
				line = amLog.readline()
				continue
			# Case: end of generic container startup
			found = re.search(r'.+INFO.+TezChild.+task.ContainerReporter: Got TaskUpdate.*', line)
			if found and "BEGIN" in generic_container_startup_status:
				generic_container_startup_status="NULL"
				found = re.search(time_string_RM, line)
				generic_container_startup=generic_container_startup[:-1]+[(generic_container_startup[-1:][0][0],getTime(found))]
				line = amLog.readline()
				continue
				
			##########DAG SPECIFIC##########
			# Case: get vertex launch order (hive name)
			found = re.search(r'.+Routing pending task events for vertex: vertex_[0-9]+_[0-9]+_[0-9]+_[0-9]+ \[(.+)\]', line)
			if found:
				#print "Going to store vertex order for "+found.group(1)
				vertex_order.append(found.group(1))
				line = amLog.readline()
				continue
			# Case: get task attempt mapping to container and implicit launch order
			found = re.search(r'.+Assigned taskAttempt.+(attempt_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+).+to container:.+(container_[0-9]+_[0-9]+_[0-9]+_[0-9]+).', line)
			if found:
				tk = found.group(1)
				cnt = found.group(2)
				task_order.append(tk)
				map_task_cnt[tk]=cnt
				map_cnt_task[cnt]=tk
				line = amLog.readline()
				continue
			# Case: build list of tasks for each vertex
			found = re.search(r'.+impl.TaskAttemptImpl: remoteTaskSpec:DAGName.+VertexName: (.+), VertexParallelism.+TaskAttemptID:(attempt_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+).+', line)
			if found:
				vx = found.group(1)
				tk = found.group(2)
				if vx in map_vx_ltk.keys():
					map_vx_ltk[vx].append(tk)
				else:
					map_vx_ltk[vx]=[tk]
				line = amLog.readline()
				continue
			# Major case: handle task attempts (get start/end time)
			#-----------------------------------------------------#
			# Case: beginning of a container log
			found = re.search(r'LogType:syslog_(attempt_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+)', line)
			if found:
				tk=found.group(1)
				# Only if we found a new task log after a previous container, finalize last container 
				#if tk not in TK_STATUS[0] and "START" in TK_STATUS[1]:
				#	tk_start_end[last_task].append(last_time)
				# Initialize the new container:
				last_task=tk
				tk_start_end[tk]=(-1,-1)
				TK_STATUS="INIT"
				line = amLog.readline()
				continue
			# Case: we are within a container log, see if it's the first timestamp we got (= container started at this time)
			if "INIT" in TK_STATUS:
				found = re.search(time_string_RM, line)
				if found:
					tk=last_task
					this_time = getTime(found)
					tk_start_end[tk]=(this_time,-1)
					TK_STATUS="START"
					last_time=this_time
					line = amLog.readline()
					continue
			if "START" in TK_STATUS:
				found = re.search(r'.+runtime.LogicalIOProcessorRuntimeTask: Final Counters.+', line)
				if found:
					cnt = current_container
					if cnt in release_am_side.keys():
						print "Container released after release? "+cnt
					generic_container_startup_status="NULL"
					found = re.search(r'.*(..):(..):(..),(...).+', line)
					this_time=getTime(found)
					release_am_side[cnt] = this_time
					#container_type[cnt]="OLD"
					current_container=""
					tk_start_end[last_task]=(tk_start_end[last_task][0],this_time)
					last_task=-99
					TK_STATUS="NULL"
					line = amLog.readline()
					continue
				else:
					line = amLog.readline()
					continue
			#-----------------------------------------------------#
			# Case: get task priority and vertex name/id mapping
			found = re.search(r'.+Triggering start event for vertex: vertex_[0-9]+_[0-9]+_[0-9]+_([0-9]+) \[(.+[0-9]+)\] with distanceFromRoot: ([0-9]+)', line)
			if found:
				vx_id = int(found.group(1))
				vx_name = found.group(2)
				low = (int(found.group(3))+1)*3
				high = low-2
				pri = (high+low)/2
				map_vx_pri[vx_name]=str(pri)
				if vx_name in map_vid_vname.keys():
					if vx_id != map_vid_vname[vx_name]:
						print "Different match vertex id - vertex name accross different run of same query: "+str(vx_id)+","+map_vid_vname[vx_name]+" for "+vx_name
						exit(-1)
				elif not isOldMapping:
					map_vid_vname[vx_name] = vx_id
				line = amLog.readline()
				continue
			#--------------------------------------------
			line = amLog.readline()
			

		########################
		#Parsing RM log, line by line #
		########################
		print "Parsing RM log"
		line = rmLog.readline()
		release_rm_side={}
		counter=0
		ast_found=False
		while line:
			counter+=1
			if counter%1000==0:
				print str(counter/1000)+"K"
			# Case: get app name
			if not ast_found:
				found = re.search(r'.+Storing application with id (application_[0-9]+_[0-9]+).*', line)
				if found:
					this_app = found.group(1)
					al.write(this_app+"\t")
					ast_found=True
					line = rmLog.readline()
					continue
			# Case: release container (any kind), RM side
			found = re.search(r'.+INFO  scheduler.SchedulerNode.+SchedulerNode.java:releaseContainer.*Released container (container_[0-9]+_[0-9]+_[0-9]+_[0-9]+).*', line)
			if found:
				cnt = found.group(1)
				found = re.search(time_string_RM, line)
				this_time = getTime(found)
				if cnt in release_rm_side.keys():
					print "Container released after release? "+cnt
				if cnt in release_am_side.keys():
					release_rm_side[cnt] = this_time
				else:
					isCnt1=re.search(r'container_[0-9]+_[0-9]+_[0-9]+_000001', cnt)
					if isCnt1:
						first_container_release=(first_container_release[0],this_time)
					else:
						print "Misterious container (not released by AM): "+cnt
				line = rmLog.readline()
				continue
			found = re.search(r'.+(container_[0-9]+_[0-9]+_[0-9]+_[0-9]+) Container Transitioned from ALLOCATED to ACQUIRED', line)
			if found:
				cnt = found.group(1)
				if cnt not in container_acquisition.keys():
					print "Container with acquisition RM-side but not AM: "+cnt
					exit(-1)
				else:
					found = re.search(time_string_RM, line)
					this_time = getTime(found)
					quadruple = container_acquisition[cnt]
					received = container_acquisition[cnt][1]
					start = container_acquisition[cnt][2]
					ctype = container_acquisition[cnt][3]
					container_acquisition[cnt]=(this_time,received,start,ctype)
				line = rmLog.readline()
				continue
			line = rmLog.readline()
			

		#########################
		# Some checks and write out #
		#########################
		if len(release_rm_side.keys()) != (len(release_am_side.keys())):
			print "Number of released container is different on RM and AM side ("+str(len(release_rm_side.keys()))+"!="+str(len(release_am_side.keys()))+")"
			print release_rm_side
			print release_am_side
		for cnt in release_am_side.keys():
			if cnt not in release_rm_side.keys():
				print "Can't find release entry on RM for "+cnt
				continue
			interval = int(release_rm_side[cnt])-int(release_am_side[cnt])
			if cnt in container_type.keys():
				rc.write(str(interval)+"\t"+container_type[cnt]+"\n")
			else:
				rc.write(str(interval)+"\tEND\n")
		for cnt in container_acquisition.keys():
			quadruple = container_acquisition[cnt]
			allocation = quadruple[0]
			acquisition = quadruple[1]
			start = quadruple[2]
			ctype = quadruple[3]
			if "GEN" in ctype:
				if allocation == -1 or acquisition == -1 or start == -1:
					print "GEN container with some unset values: "+cnt+"-"+str(allocation)+"-"+str(acquisition)+"-"+str(start)
					exit(-1)
				ca.write(str(acquisition-allocation)+"\t"+str(start-acquisition)+"\t"+ctype+"\n")
			elif "NEW" in ctype:
				if start != -1:
					print "NEW container with start value set: "+cnt
					exit(-1)
				ca.write(str(acquisition-allocation)+"\t"+ctype+"\n")
			elif "1ST" in ctype:
				if acquisition != -1:
					print "1ST container with acquisition value set!"
					exit(-1)
				ca.write(str(start-allocation)+"\t"+ctype+"\n")
		for couple in generic_container_startup:
			end = couple[1]
			start = couple[0]
			if end == -1 or start == -1:
				print "Error with couple: ("+str(start)+","+str(end)+")"
				exit(-1)
			gc.write(str(end-start)+"\t"+this_app+"\n")
		# First container: startup \t epilogue \t release \n
		if first_container_startup[0] == -1 or first_container_startup[1] == -1:
			print "Error in first_container_startup: "+str(first_container_startup)
			exit(-1)
		else:
			fc.write(str(first_container_startup[1]-first_container_startup[0])+"\t")
		if first_container_epilogue[0] == -1 or first_container_epilogue[1] == -1:
			print "Error in first_container_epilogue: "+str(first_container_epilogue)
			exit(-1)
		else:
			fc.write(str(first_container_epilogue[1]-first_container_epilogue[0])+"\t")
		if first_container_release[0] == -1 or first_container_release[1] == -1:
			print "Error in first_container_release: "+str(first_container_release)
			exit(-1)
		else:
			fc.write(str(first_container_release[1]-first_container_release[0])+"\n")

		# DAG specific
		print vertex_order
		for vx in vertex_order:
			vo.write(vx+"\t")
		vo.write("\n")
		for tk in task_order:
			otk.write(tk+"\t")
		otk.write("\n")
		for vx in map_vx_ltk.keys():
			vltk.write(vx+"\t")
			ltk=map_vx_ltk[vx]
			for tk in task_order:
				if tk in ltk:
					vltk.write(tk+"\t")
			vltk.write("\n")
		vltk.write("\n")
		for tk in tk_start_end.keys():
			couple = tk_start_end[tk]
			duration = couple[1]-couple[0]
			tdlo.write(tk+"\t"+str(duration)+"\n")
		tdlo.write("\n")
		for vx in map_vx_pri.keys():
			vpri.write(vx+"\t"+map_vx_pri[vx]+"\n")
		vpri.write("\n")

		if not isOldMapping:
			print map_vid_vname
			vmap.write(pickle.dumps(map_vid_vname))
			vmap.flush()
			vmap.close()
		rmLog.close()
		amLog.close()


	fc.flush()  
	rc.flush()
	gc.flush()
	ca.flush()
	ca.close()
	fc.close()
	rc.close()
	gc.close()
	#DAG specific
	al.flush()
	vo.flush()
	vpri.flush()
	vltk.flush()
	otk.flush()
	tdlo.flush()
	al.close()
	vo.close()
	vpri.close()
	vltk.close()
	otk.close()
	tdlo.close()
