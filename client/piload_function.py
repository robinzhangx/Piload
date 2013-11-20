import errno
import os
import sys 
import subprocess

def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def tail(f, n):
    stdin,stdout = os.popen2("tail -n "+str(n) + " "+f)
    stdin.close()
    lines = stdout.readlines(); stdout.close()
    return lines

def parseWgetLog(wget_log):
    lines = tail (wget_log, 2)
    if len(lines) < 2:
        return None
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

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
