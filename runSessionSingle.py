import time
import pyhs2
import os
import sys
import random

h2s_uri = "UNSETH2S"
databaseName = 'UNSETDB'
data = (sys.argv[1],sys.argv[2],sys.argv[3])

for line in open("config/variables.sh","r").read().splitlines():
	if line[0]!="#":
		sline = line.rstrip().split("=")
		if "HIVE_SERVER2" in sline[0]:
			h2s_uri = sline[1]
		elif "SCALE" in sline[0]:
			scale = sline[1]
		elif "DB_NAME" in sline[0]:
			databaseName = sline[1].strip("\"")
databaseName = databaseName.replace("$SCALE", scale)

username = data[0]
query = open(os.path.join(sys.path[0], "queries/"+data[2]+".sql"),"r").read().replace("\n"," ").replace(";","") # Hopefully this is enough, investigate further specific replacement
queue = data[1]

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
			cur.execute(query)
			time.sleep(random.expovariate(0.1))
			if os.path.isfile("scratch/stopSession.tmp"):
				break
		#Return column info from query
		#print cur.getSchema()
 
		#Fetch table results
		#for i in cur.fetch():
		#	print i


sys.stderr.write('Leaving session'+str(data)+'\n')

