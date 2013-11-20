import os
import sys 

def tail(f, n):
    stdin,stdout = os.popen2("tail -n "+str(n) + " "+f)
    stdin.close()
    lines = stdout.readlines(); stdout.close()
    return lines

def parseWgetLog(wget_log):
    lines = tail (wget_log, 2)
    line = lines[-2]
    fields = line.split()
    if len(fields) == 9:
	    downloadedSize = fields[0]
	    percent = fields[-3]
	    speed = fields[-2]
	    timeleft = fields[-1]
	    return {
		     'downloadedSize':downloadedSize,
		     'percent' : percent,
		     'speed' : speed,
		     'timeleft' : timeleft
		   }
    else:
        return None
