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
