import threading
import time
import pyhs2
import os
import sys

h2s_uri = "UNSETH2S"
databaseName = 'UNSETDB'
users = []
for line in open("config/variables.sh","r").read().splitlines():
	if line[1]!="#":
		sline = line.rstrip().split("=")
		if "HIVE_SERVER2" in sline[1]:
			h2s_uri = sline[2]
		elif "SCALE" in sline[1]:
			scale = sline[2]
		elif "DB_NAME" in sline[1]:
			databaseName = sline[2].strip("\"")
databaseName = databaseName.replace("$SCALE", scale)

for line in open("config/ssdata.conf","r").read().splitlines():
	sline = line.rstrip().split(" ")
	user = sline[1]
	queue = sline[2]
	query = sline[3]
	users.append((user,query,queue))

isRunning = True

class myThread (threading.Thread):
	def __init__(self, username, query, queue):
		threading.Thread.__init__(self)
		self.username = username
		self.query = query
		self.queue = queue
	def run(self):
		global isRunning
		global databaseName
		global h2s_uri
		checkIsRunning = True
		print "Starting " + self.username
		
		with pyhs2.connect(host=h2s_uri,
						port=10000,
						authMechanism='PLAIN',
						user=username,
						password='',
						database=databaseName) as conn:
			with conn.cursor() as cur:
				#Show databases
				#print cur.getDatabases()
				cur.execute("set hive.execution.engine=tez")
				cur.execute("set tez.queue.name="+queue) # This should hopefully be maintained accross several query executions within the same session
				#Execute query
				while True:
					threadLock.acquire()
					checkIsRunning = isRunning
					threadLock.release()
					if checkIsRunning:
						cur.execute(query)
						# Optional, sleep for some seconds before next query
						time.sleep(random.expovariate(0.1))
					else:
						return
				#Return column info from query
				#print cur.getSchema()
		 
				#Fetch table results
				#for i in cur.fetch():
				#	print i


## MAIN THREAD

threadLock = threading.Lock()

#Keep a thread list
threads = []

# Create new threads
for element in users:
	username = element[0]
	query = open(os.path.join(sys.path[0], "queries/"+element[1]+".sql"),"r").read().replace("\n"," ").replace(";","") # Hopefully this is enough, investigate further specific replacement
	queue = element[2]
	threadx = myThread(username, query, queue)
	threads.append(threadx)
	threadx.start()

raw_input("Press enter to send a stop request to all running sessions...")
threadLock.acquire()
isRunning = False
threadLock.release()

# Wait for all threads to complete
for t in threads:
	t.join()
print "Exiting Main Thread"
