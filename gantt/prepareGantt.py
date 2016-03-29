## Copyright 2015 Eugenio Gianniti
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

import csv
import os
import re
import sys

root_directory = sys.argv[1]

class Gantt:
  shuffle_suffix = "_SHUFFLE"
  shuffle_pattern = re.compile (r"(.*)" + shuffle_suffix)
  reduce_name = re.compile (r"Reducer (\d*)")
  gantts = 0

  def __init__ (self):
    Gantt.gantts += 1
    if __debug__:
      print "I'm Gantt number {}".format (Gantt.gantts)
    self.phases = list ()
    self.tasks = list ()
    self.tasks_per_phase = dict ()
    self.starts = dict ()
    self.ends = dict ()
    self.durations = dict ()
    self.nodes = dict ()
    self.containers = dict ()

  @staticmethod
  def generate_shuffle_id (task_id):
    return task_id + Gantt.shuffle_suffix

  def add_phase (self, phase_id):
    if phase_id not in self.phases:
      self.phases.append (phase_id)
      if __debug__:
        print "Added phase {}".format (phase_id)
      matched = Gantt.reduce_name.match (phase_id)
      if matched:
        phase_id = "Shuffle " + matched.group (1)
        self.phases.append (phase_id)
        if __debug__:
          print "Added phase {}".format (phase_id)
    else:
      if __debug__:
        print "Failed to add phase {}".format (phase_id)

  def add_task (self, phase_id, task_id):
    if phase_id in self.phases:
      self.tasks.append (task_id)
      if phase_id not in self.tasks_per_phase:
        self.tasks_per_phase[phase_id] = [task_id]
      else:
        self.tasks_per_phase[phase_id].append (task_id)
      if __debug__:
        print "Added task {} to phase {}".format (task_id, phase_id)
      matched = Gantt.reduce_name.match (phase_id)
      if matched:
        shuffle_phase = "Shuffle " + matched.group (1)
        shuffle_task = Gantt.generate_shuffle_id (task_id)
        self.tasks.append (shuffle_task)
        if shuffle_phase not in self.tasks_per_phase:
          self.tasks_per_phase[shuffle_phase] = [shuffle_task]
        else:
          self.tasks_per_phase[shuffle_phase].append (shuffle_task)
        if __debug__:
          print "Added task {} to phase {}".format (shuffle_task, shuffle_phase)
    else:
      if __debug__:
        print "Failed to add task {} to phase {}".format (task_id, phase_id)

  def set_start_time (self, task_id, start_time):
    if task_id in self.tasks:
      self.starts[task_id] = start_time
      if __debug__:
        print "Added start time to task {}".format (task_id)
    else:
      if __debug__:
        print "Failed to add start time to task {}".format (task_id)

  def set_end_time (self, task_id, end_time):
    if task_id in self.tasks:
      self.ends[task_id] = end_time
      if __debug__:
        print "Added end time to task {}".format (task_id)
    else:
      if __debug__:
        print "Failed to add end time to task {}".format (task_id)

  def set_duration (self, task_id, duration):
    if task_id in self.tasks:
      self.durations[task_id] = duration
      if __debug__:
        print "Added duration to task {}".format (task_id)
    else:
      if __debug__:
        print "Failed to add duration to task {}".format (task_id)

  def change_duration (self, task_id, difference):
    if task_id in self.tasks:
      try:
        new_duration = int (self.durations[task_id]) - int (difference)
        self.durations[task_id] = str (new_duration)
      except ValueError:
        raise RuntimeError, "ERROR: conversion error while changing duration value"
      if __debug__:
        print "Changed duration to task {}".format (task_id)
    else:
      if __debug__:
        print "Failed to change duration to task {}".format (task_id)

  def set_node (self, task_id, node):
    if task_id in self.tasks:
      self.nodes[task_id] = node
      if __debug__:
        print "Added node to task {}".format (task_id)
    else:
      if __debug__:
        print "Failed to add node to task {}".format (task_id)

  def set_container (self, task_id, container):
    if task_id in self.tasks:
      self.containers[task_id] = container
      if __debug__:
        print "Added container to task {}".format (task_id)
    else:
      if __debug__:
        print "Failed to add container to task {}".format (task_id)

  def write_csv (self, file):
    field_names = ["Phase", "Task", "Container", "Node", "Start", "End", "Duration"]
    writer = csv.DictWriter (file, fieldnames=field_names)
    writer.writeheader ()
    try:
      for phase in self.phases:
        if __debug__:
          print "Working on phase {}".format (phase)
        for task in self.tasks_per_phase[phase]:
          matched = Gantt.shuffle_pattern.match (task)
          if matched:
            alt_task = matched.group (1)
          else:
            alt_task = task
          if __debug__:
            print "Writing data of task {}".format (alt_task)
          row = {"Phase" : phase, "Task" : alt_task, "Node" : self.nodes[alt_task],
                 "Start" : self.starts[task], "End" : self.ends[task],
                 "Duration" : self.durations[task],
                 "Container" : self.containers[alt_task]}
          writer.writerow (row)
    except KeyError:
      raise RuntimeError, "ERROR: incomplete Gantt chart data"

results_dir = os.path.join (root_directory, "data")
gantts_dir = os.path.join (root_directory, "gantts")
if not os.path.exists (results_dir):
  print "ERROR: missing data directory in " + root_directory
  sys.exit (1)
if not os.path.exists (gantts_dir):
  os.mkdir (gantts_dir)

vertex_order_file = open (os.path.join (results_dir, "vertexOrder.txt"), "r")
vertex_lists_file = open (os.path.join (results_dir, "vertexLtask.txt"), "r")
task_durations_file = open (os.path.join (results_dir, "taskDurationLO.txt"), "r")
task_start_end_file = open (os.path.join (results_dir, "taskStartEnd.txt"), "r")
task_nodes_file = open (os.path.join (results_dir, "taskNode.txt"), "r")
task_containers_file = open (os.path.join (results_dir, "taskContainer.txt"), "r")
shuffle_durations_file = open (os.path.join (results_dir, "shuffleDurationLO.txt"), "r")
shuffle_start_end_file = open (os.path.join (results_dir, "shuffleStartEnd.txt"), "r")

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
    for line in shuffle_start_end_file:
      line = line.strip ()
      if line:
        looking_for = "task"
        for word in line.strip ().split ("\t"):
          word = word.strip ()
          if word:
            if looking_for == "task":
              original_task = word
              task = Gantt.generate_shuffle_id (original_task)
              looking_for = "start"
            elif looking_for == "start":
              gantt.set_start_time (task, word)
              looking_for = "end"
            elif looking_for == "end":
              gantt.set_end_time (task, word)
              gantt.set_start_time (original_task, word)
              break
      else:
        break
    for line in shuffle_durations_file:
      line = line.strip ()
      if line:
        looking_for = "task"
        for word in line.strip ().split ("\t"):
          word = word.strip ()
          if word:
            if looking_for == "task":
              original_task = word
              task = Gantt.generate_shuffle_id (original_task)
              looking_for = "duration"
            elif looking_for == "duration":
              gantt.set_duration (task, word)
              gantt.change_duration (original_task, word)
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
    for line in task_containers_file:
      line = line.strip ()
      if line:
        looking_for = "task"
        for word in line.strip ().split ("\t"):
          word = word.strip ()
          if word:
            if looking_for == "task":
              task = word
              looking_for = "container"
            elif looking_for == "container":
              gantt.set_container (task, word)
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
  task_containers_file.close ()
  shuffle_durations_file.close ()
  shuffle_start_end_file.close ()
