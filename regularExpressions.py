import re
from datetime import datetime

class App:
  def __init__ (self, app):
    self.start = re.compile (r".*Storing application with id {}.*".format (app))
    self.end = re.compile (r".*capacity.ParentQueue .+ Application removed.+appId: {}.*".format (app))

class Time:
  time = re.compile (r'([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+):([0-9]+):([0-9]+),([0-9]+).+')

  @staticmethod
  def getTime(some):
    h = int(some.group(4))*60*60*1000
    m = int(some.group(5))*60*1000
    s = int(some.group(6))*1000
    ms = int(some.group(7))
    return (h+m+s+ms)

  @staticmethod
  def dateTime(some):
    y = int(some.group(1))
    m = int(some.group(2))
    d = int(some.group(3))
    h = int(some.group(4))
    mm = int(some.group(5))
    s = int(some.group(6))
    return datetime(y,m,d,h,mm,s)

class RM:
  storing = re.compile (r'.+Storing application with id (application_[0-9]+_[0-9]+).*')
  release = re.compile (r'.+INFO  scheduler.SchedulerNode.+SchedulerNode.java:releaseContainer.*Released container (container_[0-9]+_[0-9]+_[0-9]+_[0-9]+).*')
  acquisition = re.compile (r'.+(container_[0-9]+_[0-9]+_[0-9]+_[0-9]+) Container Transitioned from ALLOCATED to ACQUIRED')
  first_container = re.compile (r'container_[0-9]+_[0-9]+_[0-9]+_000001')

  @classmethod
  def search_all (myclass, string):
    return myclass.storing.search (string) or myclass.release.search (string) or myclass.acquisition.search (string)

class AM:
  expired = re.compile (r".*No taskRequests. Container\'s idle timeout delay expired or is new. Releasing container, .*(container_[0-9]+_[0-9]+_[0-9]+_[0-9]+).*isNew=false")
  end_of_dag = re.compile (r'.*app.DAGAppMaster: Calling stop for all the services')
  stop_container = re.compile (r'.*Sending a stop request to the NM for ContainerId: (container_[0-9]+_[0-9]+_[0-9]+_[0-9]+).*')
  release_empty = re.compile (r".*No taskRequests. Container\'s idle timeout delay expired or is new. Releasing container, .*(container_[0-9]+_[0-9]+_[0-9]+_[0-9]+).*isNew=true")
  received_container = re.compile (r".*Assigning container to task, container=Container: \[ContainerId: (container_[0-9]+_[0-9]+_[0-9]+_[0-9]+).* containerHost=(\w+)")
  container_on = re.compile (r'Container: (container_[0-9]+_[0-9]+_[0-9]+_000001) on .*')
  dag_master = re.compile (r'.+app.DAGAppMaster: Created DAGAppMaster for application appattempt.*')
  starting_tasks = re.compile (r'.+impl.ImmediateStartVertexManager: Starting [0-9]+ in .+')
  end_of_dag = re.compile (r'.+impl.DAGImpl: dag_[0-9]+_[0-9]+_[0-9]+ transitioned from RUNNING to SUCCEEDED')
  end_of_epilogue = re.compile (r'.+app.DAGAppMaster: The shutdown handler has completed')
  generic_container = re.compile (r'Container: (container_[0-9]+_[0-9]+_[0-9]+_[0-9]+).+')
  starting_container = re.compile (r'.+INFO.+main.+task.TezChild: TezChild starting')
  end_of_generic_startup = re.compile (r'.+INFO.+TezChild.+task.ContainerReporter: Got TaskUpdate.*')
  vertex_launch = re.compile (r'.+Routing pending task events for vertex: vertex_[0-9]+_[0-9]+_[0-9]+_[0-9]+ \[(.+)\]')
  task_to_container = re.compile (r'.+Assigned taskAttempt.+(attempt_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+).+to container:.+(container_[0-9]+_[0-9]+_[0-9]+_[0-9]+).')
  task_to_vertex = re.compile (r'.+impl.TaskAttemptImpl: remoteTaskSpec:DAGName.+VertexName: (.+), VertexParallelism.+TaskAttemptID:(attempt_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+).+')
  log_type = re.compile (r'LogType:syslog_(attempt_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+)')
  start_vertex = re.compile (r'.+Triggering start event for vertex: vertex_[0-9]+_[0-9]+_[0-9]+_([0-9]+) \[(.+[0-9]+)\] with distanceFromRoot: ([0-9]+)')
