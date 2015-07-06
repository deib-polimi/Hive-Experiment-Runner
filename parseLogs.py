# For every query present in the list, for every app run using that query, parse the logs
# in the appropriate folder, collecting info about main time intervals and writing on several 
# files (common to the apps of a same query) info for the subsequent dag creation 
import sys
import os
import regularExpressions as myre
import shutil
from datetime import datetime
try:
  import cPickle as pickle
except:
  import pickle

#######################################
# Populate list of queries to analyze #
#######################################
query_list = []
for line in open(os.path.join(sys.path[0], "config/variables.sh"),"r").read().splitlines():
  if line and line[0] != "#":
    sline = line.split("=")
    if "QUERIES" in sline[0]:
      query_list = sline[1].strip("\"").split(" ")
      print "Working on the following queries: "+str(query_list)
      break

#########################################################################
# Outer iteration, for every query, clean/make the query results folder #
#########################################################################
for query in query_list:
  working_dir = os.path.join("fetched/"+query)
  final_result_dir = os.path.join("fetched/"+query+"/results")
  if os.path.exists(final_result_dir):
    shutil.rmtree(final_result_dir)
  os.makedirs(final_result_dir)

  #####################
  # Open output files #
  #####################
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
  tse = open (final_result_dir + "/taskStartEnd.txt", "a")
  # Map tasks to nodes
  task_to_nodes = open (os.path.join (final_result_dir, "taskNode.txt"), "a")


  #################################################################
  # For every app run for the current query, collect all the info #
  #################################################################
  try:
    with open(working_dir+"/apps_"+query+".txt","r") as apps:
      for app in apps:
        app = app.strip ()
        if not app:
          continue
        print "Working on {}".format (app)
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

        ################################
        # Parsing AM log, line by line #
        ################################
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
        # Map containers to nodes
        map_cnt_node = {}

        while line:
          counter+=1
          if counter%1000==0:
            print str(counter/1000)+"K"

          # Case: non-blocking check over container type, case expired
          found = myre.AM.expired.search (line)
          if found:
            cnt = found.group(1)
            container_type[cnt]="EXP"
          # Case: non-blocking check to be at the end of dag execution
          found = myre.AM.end_of_dag.search (line)
          if found:
            end_DAG=True
          # Case: release container request, AM side.
          # This is sent also for expired containers, not just deallocating container on dag exit.
          found = myre.AM.stop_container.search (line)
          if found:
            cnt = found.group(1)
            #print "Stopping "+cnt
            if not end_DAG:
              print "ERROR: Sending container stop request before end of dag (expired): "+cnt
              #exit(-1)
            if cnt in release_am_side.keys():
              print "Container released after release? "+cnt
            found = myre.Time.time.search (line)
            release_am_side[cnt] = myre.Time.getTime(found)
            line = amLog.readline()
            continue
          # Case: release container because new container and no task, AM side
          found = myre.AM.release_empty.search (line)
          if found:
            cnt = found.group(1)
            if cnt in release_am_side.keys():
              print "Container released after release? "+cnt
            found = myre.Time.time.search (line)
            this_time = myre.Time.getTime(found)
            release_am_side[cnt] = this_time
            if cnt in container_acquisition.keys():
              print "ERROR: Double container_acquisition for "+cnt
              #exit(-1)
            container_acquisition[cnt]=(-1,this_time,-1,"NEW")
            container_type[cnt]="NEW"
            line = amLog.readline()
            continue
          # Container received, set element in container_acquisition
          found = myre.AM.received_container.search (line)
          if found:
            cnt, host = found.group(1, 2)
            if cnt not in map_cnt_node.keys ():
              map_cnt_node[cnt] = host
            found = myre.Time.time.search (line)
            this_time = myre.Time.getTime(found)
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
            found = myre.AM.container_on.match (line)
            if found:
              current_container=found.group(1)
              first_container_startup_status="INIT"
              line = amLog.readline()
              continue
          # Case: found the beginning of the first container activity (begin of startup)
          if "INIT" in first_container_startup_status:
            found = myre.AM.dag_master.search (line)
            if found:
              found = myre.Time.time.search (line)
              this_time = myre.Time.getTime (found)
              if current_container in container_acquisition.keys():
                print "ERROR: Double container_acquisition for "+current_container
                #exit(-1)
              else:
                container_acquisition[current_container]=(-1,-1,this_time,"1ST")
              current_container = ""
              first_container_startup_status="START"
              first_container_startup=(this_time,-1)
              line = amLog.readline()
              continue
          # Case: end of container startup, it starts generating new tasks
          if "START" in first_container_startup_status:
            found = myre.AM.starting_tasks.search (line)
            if found:
              first_container_startup_status="MIDDLE"
              found = myre.Time.time.search (line)
              first_container_startup=(first_container_startup[0], myre.Time.getTime(found))
              line = amLog.readline()
              continue
          # Case: look for the the end of the dag, epilogue begins
          if "MIDDLE" in first_container_startup_status:
            found = myre.AM.end_of_dag.search (line)
            if found:
              first_container_startup_status="EPILOGUE"
              if last_time < 0:
                print "ERROR: Unexpected last_time value: "+str(last_time)
                #exit(-1)
              first_container_epilogue=(last_time,-1)
              line = amLog.readline()
              continue
            else:
              found = myre.Time.time.search (line)
              if found:
                last_time = myre.Time.getTime (found)
              # no continue here, this line could be in following checks
          # Case: last entry for first container log, end of epilogue, beginning of first container release
          if "EPILOGUE" in first_container_startup_status:
            found = myre.AM.end_of_epilogue.search (line)
            if found:
              first_container_startup_status="END"
              found = myre.Time.time.search (line)
              last_time = myre.Time.getTime(found)
              first_container_epilogue=(first_container_epilogue[0],last_time)
              first_container_release=(last_time,-1)
              line = amLog.readline()
              continue
          #--------------------------------------------

          # Case: generic container
          found = myre.AM.generic_container.search (line)
          if found:
            current_container=found.group(1)
            line = amLog.readline()
            continue
          # Case: container just started
          found = myre.AM.starting_container.search (line)
          if found:
            if "NULL" not in generic_container_startup_status:
              print "ERROR: Unexpected status of first_container_startup_status: "+generic_container_startup_status
              #exit(-1)
            generic_container_startup_status="BEGIN"
            found = myre.Time.time.search (line)
            this_time = myre.Time.getTime(found)
            generic_container_startup.append((this_time,-1))
            if current_container in container_acquisition.keys():
              container_acquisition[current_container]=(-1,container_acquisition[current_container][1],this_time,"GEN")
            else:
              container_acquisition[current_container]=(-1,-1,this_time,"GEN")
            current_container=""
            line = amLog.readline()
            continue
          # Case: end of generic container startup
          found = myre.AM.end_of_generic_startup.search (line)
          if found and "BEGIN" in generic_container_startup_status:
            generic_container_startup_status="NULL"
            found = myre.Time.time.search (line)
            generic_container_startup=generic_container_startup[:-1]+[(generic_container_startup[-1:][0][0],myre.Time.getTime(found))]
            line = amLog.readline()
            continue

          ##########DAG SPECIFIC##########
          # Case: get vertex launch order (hive name)
          found = myre.AM.vertex_launch.search (line)
          if found:
            #print "Going to store vertex order for "+found.group(1)
            vertex_order.append(found.group(1))
            line = amLog.readline()
            continue
          # Case: get task attempt mapping to container and implicit launch order
          found = myre.AM.task_to_container.search (line)
          if found:
            tk = found.group(1)
            cnt = found.group(2)
            task_order.append(tk)
            map_task_cnt[tk]=cnt
            map_cnt_task[cnt]=tk
            line = amLog.readline()
            continue
          # Case: build list of tasks for each vertex
          found = myre.AM.task_to_vertex.search (line)
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
          found = myre.AM.log_type.search (line)
          if found:
            tk=found.group(1)
            # Only if we found a new task log after a previous container, finalize last container 
            #if tk not in TK_STATUS[0] and "START" in TK_STATUS[1]:
            #  tk_start_end[last_task].append(last_time)
            # Initialize the new container:
            last_task=tk
            tk_start_end[tk]=(-1,-1)
            TK_STATUS="INIT"
            line = amLog.readline()
            continue
          # Case: we are within a container log, see if it's the first timestamp we got (= container started at this time)
          if "INIT" in TK_STATUS:
            found = myre.Time.time.search (line)
            if found:
              tk=last_task
              this_time = myre.Time.getTime(found)
              tk_start_end[tk]=(this_time,-1)
              TK_STATUS="START"
              last_time=this_time
              line = amLog.readline()
              continue
          if "START" in TK_STATUS:
            if line=="\n":
              tk_start_end[last_task]=(tk_start_end[last_task][0],last_time)
              last_task=-99
              last_time=-99
              TK_STATUS="NULL"
              line = amLog.readline()
              continue
            else:
              found = myre.Time.time.search (line)
              if found:
                last_time=myre.Time.getTime(found)
                line = amLog.readline()
                continue
          #-----------------------------------------------------#
          # Case: get task priority and vertex name/id mapping
          found = myre.AM.start_vertex.search (line)
          if found:
            vx_id = int(found.group(1))
            vx_name = found.group(2)
            low = (int(found.group(3))+1)*3
            high = low-2
            pri = (high+low)/2
            map_vx_pri[vx_name]=str(pri)
            if vx_name in map_vid_vname.keys():
              if vx_id != map_vid_vname[vx_name]:
                print "ERROR: Different match vertex id - vertex name accross different run of same query: "+str(vx_id)+","+map_vid_vname[vx_name]+" for "+vx_name
                #exit(-1)
            elif not isOldMapping:
              map_vid_vname[vx_name] = vx_id
            line = amLog.readline()
            continue
          #--------------------------------------------
          line = amLog.readline()

        ###############################
        #Parsing RM log, line by line #
        ###############################
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
            found = myre.RM.storing.search (line)
            if found:
              this_app = found.group(1)
              al.write(this_app+"\t")
              ast_found=True
              line = rmLog.readline()
              continue
          # Case: release container (any kind), RM side
          found = myre.RM.release.search (line)
          if found:
            cnt = found.group(1)
            found = myre.Time.time.search (line)
            this_time = myre.Time.getTime (found)
            if cnt in release_rm_side.keys():
              print "Container released after release? "+cnt
            if cnt in release_am_side.keys():
              release_rm_side[cnt] = this_time
            else:
              isCnt1 = myre.RM.first_container.search (cnt)
              if isCnt1:
                first_container_release=(first_container_release[0],this_time)
              else:
                print "Misterious container (not released by AM): "+cnt
            line = rmLog.readline()
            continue
          found = myre.RM.acquisition.search (line)
          if found:
            cnt = found.group(1)
            if cnt not in container_acquisition.keys():
              print "ERROR: Container with acquisition RM-side but not AM: "+cnt
              #exit(-1)
            else:
              found = myre.Time.time.search (line)
              this_time = myre.Time.getTime (found)
              quadruple = container_acquisition[cnt]
              received = container_acquisition[cnt][1]
              start = container_acquisition[cnt][2]
              ctype = container_acquisition[cnt][3]
              container_acquisition[cnt]=(this_time,received,start,ctype)
            line = rmLog.readline()
            continue
          line = rmLog.readline()

        #############################
        # Some checks and write out #
        #############################
        if len(release_rm_side.keys()) != (len(release_am_side.keys())):
          print "Number of released container is different on RM and AM side ("+str(len(release_rm_side.keys()))+"!="+str(len(release_am_side.keys()))+")"
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
              print "ERROR: GEN container with some unset values: "+cnt+"-"+str(allocation)+"-"+str(acquisition)+"-"+str(start)
              #exit(-1)
            ca.write(str(acquisition-allocation)+"\t"+str(start-acquisition)+"\t"+ctype+"\n")
          elif "NEW" in ctype:
            if start != -1:
              print "ERROR: NEW container with start value set: "+cnt
              #exit(-1)
            ca.write(str(acquisition-allocation)+"\t"+ctype+"\n")
          elif "1ST" in ctype:
            if acquisition != -1:
              print "ERROR: 1ST container with acquisition value set!"
              #exit(-1)
            ca.write(str(start-allocation)+"\t"+ctype+"\n")
        for couple in generic_container_startup:
          end = couple[1]
          start = couple[0]
          if end == -1 or start == -1:
            print "ERROR: Error with couple: ("+str(start)+","+str(end)+")"
            #exit(-1)
          gc.write(str(end-start)+"\t"+this_app+"\n")
        # First container: startup \t epilogue \t release \n
        if first_container_startup[0] == -1 or first_container_startup[1] == -1:
          print "ERROR: Error in first_container_startup: "+str(first_container_startup)
          #exit(-1)
        else:
          fc.write(str(first_container_startup[1]-first_container_startup[0])+"\t")
        if first_container_epilogue[0] == -1 or first_container_epilogue[1] == -1:
          print "ERROR: Error in first_container_epilogue: "+str(first_container_epilogue)
          #exit(-1)
        else:
          fc.write(str(first_container_epilogue[1]-first_container_epilogue[0])+"\t")
        if first_container_release[0] == -1 or first_container_release[1] == -1:
          print "ERROR: Error in first_container_release: "+str(first_container_release)
          #exit(-1)
        else:
          fc.write(str(first_container_release[1]-first_container_release[0])+"\n")

        # DAG specific
        print vertex_order
        for vx in vertex_order:
          vo.write(vx+"\t")
        vo.write("\n")
        for tk in task_order:
          otk.write(tk+"\t")
          node = map_cnt_node[map_task_cnt[tk]]
          task_to_nodes.write ("{Task}\t{Node}\n".format (Task=tk, Node=node))
        otk.write("\n")
        task_to_nodes.write ("\n")
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
          tse.write (tk + "\t" + str (couple[0]) + "\t" + str (couple[1]) + "\n")
        tdlo.write("\n")
        tse.write ("\n")
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

  finally:
    ca.close()
    fc.close()
    rc.close()
    gc.close()
    #DAG specific
    al.close()
    vo.close()
    vpri.close()
    vltk.close()
    otk.close()
    tdlo.close()
    tse.close ()
    task_to_nodes.close ()
