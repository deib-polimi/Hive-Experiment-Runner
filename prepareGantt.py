import sys
import os

query_list = []
for line in open (os.path.join(sys.path[0], "config/variables.sh"), "r").read ().splitlines ():
  if line and line[0] != "#":
    sline = line.split ("=")
    if "QUERIES" in sline[0]:
      query_list = sline[1].strip ("\"").split (" ")
      print "Working on the following queries: " + str (query_list)
      break

class Gantt:
  def __init__ (self):
    self.phases = list ()
    self.tasks = dict ()
    self.starts = dict ()
    self.ends = dict ()
    self.durations = dict ()
  
  def add_phase (self, phase_id):
    if phase_id not in self.phases:
      self.phases.append (phase_id)
  
  def add_task (self, phase_id, task_id):
    if phase_id in self.phases:
      if phase_id not in self.tasks:
        self.tasks[phase_id] = [task_id]
      else:
        self.tasks[phase_id].append (task_id)
  
  def set_start_time (self, task_id, start_time):
    if task_id in self.tasks.values ():
      self.starts[task_id] = start_time
  
  def set_end_time (self, task_id, end_time):
    if task_id in self.tasks.values ():
      self.ends[task_id] = end_time
  
  def set_duration (self, task_id, duration):
    if task_id in self.tasks.values ():
      self.durations[task_id] = duration
  
  def write_csv (self, file):
    file.write ("Phase,Task,Start,End,Duration\n")
    try:
      for phase in self.phases:
        for task in self.tasks[phase]:
          line = "{P},{T},{S},{E},{D}\n".format (P = phase, T = task,
                                                 S = self.starts[task],
                                                 E = self.ends[task],
                                                 D = self.durations[task])
          file.write (line)
    except KeyError:
      raise RuntimeError, "ERROR: incomplete Gantt chart data"
    file.flush ()

for query in query_list:
  results_dir = os.path.join ("fetched/" + query + "/results")
  gantts_dir = os.path.join ("fetched/" + query + "/gantts")
  if not os.path.exists (results_dir):
    print "ERROR: missing results directory for " + query
    continue
  if not os.path.exists (gantts_dir):
    os.mkdir (gantts_dir)
  
  vertex_order_file = open (os.path.join (results_dir, "vertexOrder.txt"), "r")
  vertex_lists_file = open (os.path.join (results_dir, "vertexLtask.txt"), "r")
  task_durations_file = open (os.path.join (results_dir, "taskDurationLO.txt"), "r")
  task_start_end_file = open (os.path.join (results_dir, "taskStartEnd.txt"), "r")
  
  try:
    counter = 0
    for job in vertex_order_file:
      gantt = Gantt ()
      for phase in job.strip ().split ("\t"):
        gantt.add_phase (phase.strip ())
      for line in vertex_lists_file:
        if line:
          phase, separator, line = line.partition ("\t")
          phase = phase.strip ()
          for task in line.strip (). split ("\t"):
            gantt.add_task (phase, task.strip ())
        else:
          break
      for line in task_start_end_file:
        if line:
          looking_for = "task"
          for word in line.strip ().split ("\t"):
            if word:
              if looking_for == "task":
                task = word.strip ()
                looking_for = "start"
              else if looking_for == "start":
                gantt.set_start_time (task, word.strip ())
                looking_for = "end"
              else if looking_for == "end":
                gantt.set_end_time (task, word.strip ())
                break
        else:
          break
      for line in task_durations_file:
        if line:
          looking_for = "task"
          for word in line.strip ().split ("\t"):
            if word:
              if looking_for == "task":
                task = word.strip ()
                looking_for = "duration"
              else if looking_for == "duration":
                gantt.set_duration (task, word.strip ())
                break
        else:
          break
      filename = "gantt{0:06d}.csv".format (counter)
      counter += 1
      gantt_file = open (os.path.join (gantts_dir, filename), "w")
      try:
        gantt.write_csv (gantt_file)
      except RuntimeError:
        print sys.exc_info ()[1]
      finally:
        gantt_file.close ()
  
  finally:
    vertex_order_file.close ()
    vertex_lists_file.close ()
    task_durations_file.close ()
    task_start_end_file.close ()
