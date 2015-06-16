from datetime import datetime
import re

verbose = True

YEAR = "UNSET"
GANGLIA_SAMPLE_RATE = "UNSET"
DSTAT_SAMPLE_RATE = "UNSET"

tracker = ""

for line in open("config/python.conf","r").read().splitlines():
	sline = line.rstrip().split(" ")
	if "YEAR" in sline[1]:
		YEAR = int(sline[2])
	elif "GANGLIA_SAMPLE_RATE" in sline[1]:
		GANGLIA_SAMPLE_RATE = int(sline[2])
	elif "DSTAT_SAMPLE_RATE" in sline[1]:
		DSTAT_SAMPLE_RATE = int(sline[2]) 

ganglia_time = r'([0-9]+)-([0-9]+)-([0-9]+)T([0-9]+):([0-9]+):([0-9]+).+'
dstat_time = r'([0-9]+)-([0-9]+) ([0-9]+):([0-9]+):([0-9]+)'

# Get timestamp as string
def dateTimeMulti(timestamp,type="ganglia"):
	global tracker
	some = re.search(ganglia_time, timestamp) if "ganglia" in type else re.search(dstat_time, timestamp)
	if not some:
		print "Can't find a proper timestamp in: "+timestamp+" of type: "+type
		print tracker
	if "ganglia" in type:
		y = int(some.group(1))
		m = int(some.group(2))
		d = int(some.group(3))
		h = int(some.group(4))
		mm = int(some.group(5))
		s = int(some.group(6))
	elif "dstat" in type:
		y = YEAR
		d = int(some.group(1))
		m = int(some.group(2))
		h = int(some.group(3))
		mm = int(some.group(4))
		s = int(some.group(5))
	else:
		print "Wrong type "+type
		exit(-1)
	return datetime(y,m,d,h,mm,s)

# Get string, return string
def cleanHeader(content):
	# Skip first lines, find header
	last_line = ""
	content = content.splitlines()
	this_line = content[0]
	for i in range(0,len(content)):
		this_line = content[i]
		if len(this_line)<1:
			continue
		if this_line[0].isdigit():
			header = last_line.replace('\\g', '')
			content = [header]+content[i:]
			#print "Found header: "+header
			#print "before line: "+this_line
			break
		else:
			last_line = this_line
			#print "skipping line: "+this_line
	return "\n".join(content)

# Get string, return string
def getSlice(content,start,end,type='ganglia'):
	global GANGLIA_SAMPLE_RATE
	global DSTAT_SAMPLE_RATE
	# Header should be clean already, but do it for safety
	cleanHeader(content)
	#Skip header
	scontent = content.split("\n")
	header = scontent[0]
	data = scontent[1:]
	begun = False
	finished = False
	extracted = []
	for line in data:
		timestamp = line.split(",")[0]
		this_time = dateTimeMulti(timestamp,type)
		if not begun:
			difference = start - this_time 
			difference = difference.total_seconds() - GANGLIA_SAMPLE_RATE if "ganglia" in type else difference.total_seconds() - DSTAT_SAMPLE_RATE
			if difference > 0:
				continue
			else:
				begun=True
		elif begun and not finished:
			difference = end - this_time
			difference = difference.total_seconds()
			if difference <= 0:
				gfinished=True
				if verbose:
					print "End!"
				extracted.append(line)
				break
			extracted.append(line)
	if not gfinished:
		print "Something odd happened, the app end and/or start time could not be found in ganglia metrics"
		print target_url 
		print dt_start
		print this_time
		print dt_end
	return "\n".join([header]+extracted)

def getDstatElements(driver_line):
	sline = driver_line.split(",")
	if len(sline) != 15:
		print "line has too many or few fields, check: "+driver_line
		exit(-1)
	return (dateTimeMulti(sline[0],'dstat'),float(sline[1]),float(sline[2]),float(sline[3]),float(sline[4]),float(sline[5]),float(sline[6]),int(float(sline[7])),int(float(sline[8])),int(float(sline[9])),int(float(sline[10])),int(float(sline[11])),int(float(sline[12])),int(float(sline[13])),int(float(sline[14])))

def variablesToCSVLine(agg_time, agg_cpuUsr, agg_cpuSys, agg_cpuIdl, agg_cpuWai, agg_cpuHiq, agg_cpuSiq, agg_memUsd, agg_memBuf, agg_memCac, agg_memFre, agg_netRec, agg_netSen, agg_dskRea, agg_dksWrt):
	csv_string = ""
	csv_string += str(agg_time.day).zfill(2)+"-"+str(agg_time.month).zfill(2)+" "
	csv_string += str(agg_time.hour).zfill(2)+":"+str(agg_time.minute).zfill(2)+":"+str(agg_time.second).zfill(2)+","
	csv_string += str(agg_cpuUsr)+","
	csv_string += str(agg_cpuSys)+","
	csv_string += str(agg_cpuIdl)+","
	csv_string += str(agg_cpuWai)+","
	csv_string += str(agg_cpuHiq)+","
	csv_string += str(agg_cpuSiq)+","
	csv_string += str(agg_memUsd)+","
	csv_string += str(agg_memBuf)+","
	csv_string += str(agg_memCac)+","
	csv_string += str(agg_memFre)+","
	csv_string += str(agg_netRec)+","
	csv_string += str(agg_netSen)+","
	csv_string += str(agg_dskRea)+","
	csv_string += str(agg_dksWrt)
	return csv_string

# Get list of strings, return string, just for dstat
def aggregateCsv(list_csv):
	if len(list_csv)<2:
		print "Trying to aggregate less than 2 csv files"
		return ""
	global DSTAT_SAMPLE_RATE
	global tracker
	l_triple = [] # Contains (a single csv line by line, current line, total length)
	aggregated_csv = [] # Final CSV line by line
	aggregated_csv.append(list_csv[0].split("\n")[0]) # Init with header
	# Populate l_triple
	# For every csv we have...
	for c in list_csv:
		# ...split it line by line
		sc = c.split("\n")
		# Automatically skip the line with the header, so we can start from index 0
		sc = sc[1:]
		l_triple.append([sc, 0, len(sc)])
	# Get index of driver csv
	driver_dt = datetime.now()
	driver_index = -1
	# Look for the csv with lowest time in next (first) line to be considered, it's the driver
	for i in range(0,len(l_triple)):
		this_triple = l_triple[i]
		this_csv = this_triple[0]
		this_index = this_triple[1]
		tracker = this_csv[this_index]
		this_ts = this_csv[this_index].split(",")[0]
		this_dt = dateTimeMulti(this_ts,"dstat")
		if this_dt < driver_dt:
			driver_dt = this_dt
			driver_index = i
		#else:
			#print "Passing: "+str(this_dt)+" - "+str(driver_dt) 
	if driver_index < 0:
		print "Error, driver element not found"
		exit(-1)
	# Extract driver element and update list of triples
	driver_triple = l_triple[driver_index]
	del l_triple[driver_index]
	check_aggregate = []
	# Parse driver csv lines one by one aggregating with other csv
	for driver_line in driver_triple[0]:
		res = getDstatElements(driver_line)
		d_ts = res[0]
		d_cpuUsr = res[1]
		d_cpuSys = res[2]
		d_cpuIdl = res[3]
		d_cpuWai = res[4]
		d_cpuHiq = res[5]
		d_cpuSiq = res[6]
		d_memUsd = res[7]
		d_memBuf = res[8]
		d_memCac = res[9]
		d_memFre = res[10]
		d_netRec = res[11]
		d_netSen = res[12]
		d_dskRea = res[13]
		d_dksWrt = res[14]
		num_aggregated = 1 # At least we have the driver value to copy
		agg_cpuUsr = d_cpuUsr
		agg_cpuSys = d_cpuSys
		agg_cpuIdl = d_cpuIdl
		agg_cpuWai = d_cpuWai
		agg_cpuHiq = d_cpuHiq
		agg_cpuSiq = d_cpuSiq
		agg_memUsd = d_memUsd
		agg_memBuf = d_memBuf
		agg_memCac = d_memCac
		agg_memFre = d_memFre
		agg_netRec = d_netRec
		agg_netSen = d_netSen
		agg_dskRea = d_dskRea
		agg_dksWrt = d_dksWrt
		for element in l_triple:
			this_index = element[1]
			#print "This index: "+str(this_index)
			this_length = element[2]
			if this_index >= this_length:
				print "End of file at "+str(this_index)
				continue
			this_line = element[0][this_index]
			sthis_line = this_line.split(",")
			this_time = dateTimeMulti(sthis_line[0],'dstat')
			time_diff = this_time-d_ts
			time_diff = time_diff.total_seconds()
			#print time_diff
			if ((time_diff <= 0 and abs(time_diff) <= float(DSTAT_SAMPLE_RATE)/2) or (time_diff > 0 and time_diff < float(DSTAT_SAMPLE_RATE)/2)):
				#print "inside"
				num_aggregated += 1
				this_res = getDstatElements(this_line)
		                this_ts = this_res[0]
		                this_cpuUsr = this_res[1]    
		                this_cpuSys = this_res[2]
		                this_cpuIdl = this_res[3]
		                this_cpuWai = this_res[4]
		                this_cpuHiq = this_res[5]
		                this_cpuSiq = this_res[6]
		                this_memUsd = this_res[7]
		                this_memBuf = this_res[8]
		                this_memCac = this_res[9]
                		this_memFre = this_res[10]   
		                this_netRec = this_res[11]
		                this_netSen = this_res[12]
		                this_dskRea = this_res[13]   
                		this_dksWrt = this_res[14]
				agg_cpuUsr += this_cpuUsr
				agg_cpuSys += this_cpuSys
				agg_cpuIdl += this_cpuIdl
				agg_cpuWai += this_cpuWai
				agg_cpuHiq += this_cpuHiq
				agg_cpuSiq += this_cpuSiq
				agg_memUsd += this_memUsd
				agg_memBuf += this_memBuf
				agg_memCac += this_memCac
				agg_memFre += this_memFre
				agg_netRec += this_netRec
				agg_netSen += this_netSen
				agg_dskRea += this_dskRea
				agg_dksWrt += this_dksWrt
				# Update the index of the next line to read
				element[1]+=1
			else:
				print str(this_time)+" :: "+str(d_ts)
				exit(1)
				continue
		check_aggregate.append(num_aggregated)  # Occhio che questi dovrebbero essere = 5 ogni volta, tranne i primi e gli ultimi al piu'
		agg_cpuUsr /= num_aggregated
		agg_cpuSys /= num_aggregated
		agg_cpuIdl /= num_aggregated
		agg_cpuWai /= num_aggregated
		agg_cpuHiq /= num_aggregated
		agg_cpuSiq /= num_aggregated
		aggregated_csv.append(variablesToCSVLine(d_ts, agg_cpuUsr, agg_cpuSys, agg_cpuIdl, agg_cpuWai, agg_cpuHiq, agg_cpuSiq, agg_memUsd, agg_memBuf, agg_memCac, agg_memFre, agg_netRec, agg_netSen, agg_dskRea, agg_dksWrt))
	print check_aggregate
	return "\n".join(aggregated_csv)
		
		
		
		
