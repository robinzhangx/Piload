#!/usr/bin/env python

import urllib2
import urllib
import json
import subprocess
import time
import logging
import sys
import re
import ConfigParser

TOKEN = None
INTERVAL = 10
CFG_SECTION = "piload"
STATS_LINE_REGEX = " >.+\\n"
STATS_LINE_PATTERN = re.compile(STATS_LINE_REGEX)

config = ConfigParser.RawConfigParser()
config.read('/home/pi/piload_client.cfg')

SERVER = config.get(CFG_SECTION, "server")
#SERVER = "http://127.0.0.1:8000/"
USERNAME = config.get(CFG_SECTION, "username")
PASSWORD = config.get(CFG_SECTION, "password")
AMULE_PASSWORD = config.get(CFG_SECTION, "amule_password")

logger = logging.getLogger('piload')
hdlr = logging.FileHandler('/home/pi/piload_client.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

def getToken():
    logger.info("getToken")
    url = SERVER + "api-token-auth/"
    params = urllib.urlencode({
            'username': USERNAME,
            'password': PASSWORD
    })
    data = json.load(urllib2.urlopen(url, params))
    logger.info(data)
    return data.get('token')

def getNewTask():
    logger.info("getNewTask")
    url = SERVER + "api/task/?format=json&status=N"
    req = urllib2.Request(url)
    req.add_header("Authorization", "Token " + TOKEN)
    try:
        tasks = json.load(urllib2.urlopen(req))
        return tasks
    except urllib2.URLError, e:
        logger.error(e)
        return []

def setTaskRunning(task):
    logger.info("setTaskRunning")
    if task is not None:
        url = SERVER + "api/task/" + str(task.get("id")) + "/"
        data = json.dumps({
            'status': 'R'
        })
        logger.info(data)
        req = urllib2.Request(url, data)
        req.add_header("Authorization", "Token " + TOKEN)
        req.add_header('Content-Type', 'application/json')
        req.get_method = lambda: 'PATCH'
        try:
            resp = urllib2.urlopen(req)
            logger.info(resp)
        except urllib2.HTTPError, e:
            logger.error(e)

def getStatus():
    logger.info("getStatus")
    url = SERVER + "api/status/?format=json"
    req = urllib2.Request(url)
    req.add_header("Authorization", "Token " + TOKEN)
    try:
        status = json.load(urllib2.urlopen(req))
        return status
    except urllib2.URLError, e:
        logger.error(e)
        return []

def uploadStatus(id, status):
    logger.info("uploadStatus")
    url = SERVER + "api/status/%d/" % id
    data = json.dumps({
        'status': status
    })
    req = urllib2.Request(url, data)
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header('Content-Type', 'application/json')
    req.get_method = lambda: 'PATCH'
    try:
        resp = urllib2.urlopen(req)
        logger.info(resp)
    except urllib2.HTTPError, e:
        logger.error(e)

def getDownload():
    logger.info("getDownload")
    url = SERVER + "api/download/?format=json"
    req = urllib2.Request(url)
    req.add_header("Authorization", "Token " + TOKEN)
    try:
        download = json.load(urllib2.urlopen(req))
        return download
    except urllib2.URLError, e:
        logger.error(e)
        return []

def uploadDownload(id, downloads):
    logger.info("uploadDownload")
    url = SERVER + "api/download/%d/" % id
    data = json.dumps({
        'downloads': downloads
    })
    req = urllib2.Request(url, data)
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header('Content-Type', 'application/json')
    req.get_method = lambda: 'PATCH'
    try:
        resp = urllib2.urlopen(req)
        logger.info(resp)
    except urllib2.HTTPError, e:
        logger.error(e)

def getStatsLine(input):
    stats = ""
    for m in STATS_LINE_PATTERN.finditer(input):
        stats += m.group(0)
    return stats

def getMuleStatus():
    logger.info("getMuleStatus")
    ret = ""
    try:
        status = subprocess.check_output(["amulecmd", "-P", AMULE_PASSWORD, "-c", "status"])
        ret = getStatsLine(status)
    except subprocess.CalledProcessError, e:
        logger.error(e)
    
    return ret

def getMuleDownload():
    logger.info("getMuleDownload")
    ret = ""
    try:
        downloads = subprocess.check_output(["amulecmd", "-P", AMULE_PASSWORD, "-c", "show dl"])
        ret = getStatsLine(downloads)
    except subprocess.CalledProcessError, e:
        logger.error(e)
    return ret

def addDownload(link):
    logger.info("addDownload")
    ret = subprocess.check_output(["amulecmd", "-P", AMULE_PASSWORD, "-c", "add " + link])
    logger.info(ret)

def run():
    tasks = getNewTask();
    for t in tasks:
        uri = t.get("uri")
        logger.info(uri)
        addDownload(uri)
        setTaskRunning(t)
    statuss = getStatus()
    if len(statuss) >= 1:
        uploadStatus(statuss[0].get("id"), getMuleStatus())
    downloads = getDownload()
    if len(downloads) >= 1:
        uploadDownload(downloads[0].get("id"), getMuleDownload())

TOKEN = getToken()
while True:
    #try:
        logger.info("run")
        run()
        time.sleep(INTERVAL)
    #except Exception, e:
    #    logger.error("Unexpected error:" + e)
    #    raise
