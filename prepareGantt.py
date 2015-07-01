import sys
import os
import csv

query_list = []
for line in open (os.path.join(sys.path[0], "config/variables.sh"), "r").read ().splitlines ():
  if line and line[0] != "#":
    sline = line.split ("=")
    if "QUERIES" in sline[0]:
      query_list = sline[1].strip ("\"").split (" ")
      print "Working on the following queries: " + str (query_list)
      break

do_debug = (os.getenv ("DEBUG", "no") == "yes")

class Gantt:
  gantts = 0
  
  def __init__ (self):
    Gantt.gantts += 1
    if do_debug:
      print "I'm Gantt number {}".format (Gantt.gantts)
    self.phases = list ()
    self.tasks = list ()
    self.tasks_per_phase = dict ()
    self.starts = dict ()
    self.ends = dict ()
    self.durations = dict ()
    self.nodes = dict ()
  
  def add_phase (self, phase_id):
    if phase_id not in self.phases:
      self.phases.append (phase_id)
      if do_debug:
        print "Added phase {}".format (phase_id)
    else:
      if do_debug:
        print "Failed to add phase {}".format (phase_id)
  
  def add_task (self, phase_id, task_id):
    if phase_id in self.phases:
      self.tasks.append (task_id)
      if phase_id not in self.tasks_per_phase:
        self.tasks_per_phase[phase_id] = [task_id]
      else:
        self.tasks_per_phase[phase_id].append (task_id)
      if do_debug:
        print "Added task {} to phase {}".format (task_id, phase_id)
    else:
      if do_debug:
        print "Failed to add task {} to phase {}".format (task_id, phase_id)
  
  def set_start_time (self, task_id, start_time):
    if task_id in self.tasks:
      self.starts[task_id] = start_time
      if do_debug:
        print "Added start time to task {}".format (task_id)
    else:
      if do_debug:
        print "Failed to add start time to task {}".format (task_id)
  
  def set_end_time (self, task_id, end_time):
    if task_id in self.tasks:
      self.ends[task_id] = end_time
      if do_debug:
        print "Added end time to task {}".format (task_id)
    else:
      if do_debug:
        print "Failed to add end time to task {}".format (task_id)
  
  def set_duration (self, task_id, duration):
    if task_id in self.tasks:
      self.durations[task_id] = duration
      if do_debug:
        print "Added duration to task {}".format (task_id)
    else:
      if do_debug:
        print "Failed to add duration to task {}".format (task_id)
  
  def set_node (self, task_id, node):
    if task_id in self.tasks:
      self.nodes[task_id] = node
      if do_debug:
        print "Added node to task {}".format (task_id)
    else:
      if do_debug:
        print "Failed to add node to task {}".format (task_id)
  
  def write_csv (self, file):
    field_names = ["Phase", "Task", "Node", "Start", "End", "Duration"]
    writer = csv.DictWriter (file, fieldnames=field_names)
    writer.writeheader ()
    try:
      for phase in self.phases:
        if do_debug:
          print "Working on phase {}".format (phase)
        for task in self.tasks_per_phase[phase]:
          if do_debug:
            print "Writing data of task {}".format (task)
          row = {"Phase" : phase, "Task" : task, "Node" : self.nodes[task],
                 "Start" : self.starts[task], "End" : self.ends[task],
                 "Duration" : self.durations[task]}
          writer.writerow (row)
    except KeyError:
      raise RuntimeError, "ERROR: incomplete Gantt chart data"

for query in query_list:
  results_dir = os.path.join ("fetched", query, "results")
  gantts_dir = os.path.join ("fetched", query, "gantts")
  if not os.path.exists (results_dir):
    print "ERROR: missing results directory for " + query
    continue
  if not os.path.exists (gantts_dir):
    os.mkdir (gantts_dir)
  
  vertex_order_file = open (os.path.join (results_dir, "vertexOrder.txt"), "r")
  vertex_lists_file = open (os.path.join (results_dir, "vertexLtask.txt"), "r")
  task_durations_file = open (os.path.join (results_dir, "taskDurationLO.txt"), "r")
  task_start_end_file = open (os.path.join (results_dir, "taskStartEnd.txt"), "r")
  task_nodes_file = open (os.path.join (results_dir, "taskNode.txt"), "r")
  
  try:
    counter = 0
    for job in vertex_order_file:
      gantt = Gantt ()
      for phase in job.strip ().split ("\t"):
        phase = phase.strip ()
        if phase:
          gantt.add_phase (phase)
      for line in vertex_lists_file:
        line = line.strip ()
        if line:
          phase, separator, line = line.partition ("\t")
          phase = phase.strip ()
          for task in line.strip ().split ("\t"):
            task = task.strip ()
            if task:
              gantt.add_task (phase, task)
        else:
          break
      for line in task_start_end_file:
        line = line.strip ()
        if line:
          looking_for = "task"
          for word in line.strip ().split ("\t"):
            word = word.strip ()
            if word:
              if looking_for == "task":
                task = word
                looking_for = "start"
              elif looking_for == "start":
                gantt.set_start_time (task, word)
                looking_for = "end"
              elif looking_for == "end":
                gantt.set_end_time (task, word)
                break
        else:
          break
      for line in task_durations_file:
        line = line.strip ()
        if line:
          looking_for = "task"
          for word in line.strip ().split ("\t"):
            word = word.strip ()
            if word:
              if looking_for == "task":
                task = word
                looking_for = "duration"
              elif looking_for == "duration":
                gantt.set_duration (task, word)
                break
        else:
          break
      for line in task_nodes_file:
        line = line.strip ()
        if line:
          looking_for = "task"
          for word in line.strip ().split ("\t"):
            word = word.strip ()
            if word:
              if looking_for == "task":
                task = word
                looking_for = "node"
              elif looking_for == "node":
                gantt.set_node (task, word)
                break
        else:
          break
      filename = "gantt{0:06d}.csv".format (counter)
      counter += 1
      with open (os.path.join (gantts_dir, filename), "w") as gantt_file:
        try:
          gantt.write_csv (gantt_file)
        except RuntimeError:
          print sys.exc_info ()[1]
  
  finally:
    vertex_order_file.close ()
    vertex_lists_file.close ()
    task_durations_file.close ()
    task_start_end_file.close ()
    task_nodes_file.close ()
