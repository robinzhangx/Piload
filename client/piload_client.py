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
import socket
import os
from os.path import expanduser
from piload_function import parseWgetLog, cmd_exists, mkdir_p

TOKEN = None

INTERVAL = 10
CFG_SECTION = "piload"
STATS_LINE_REGEX = " >.+\\n"
STATS_LINE_PATTERN = re.compile(STATS_LINE_REGEX)
TIMEOUT = 10

config = ConfigParser.RawConfigParser()
config.read(expanduser('~/piload_client.cfg'))

SERVER = config.get(CFG_SECTION, "server")
#SERVER = "http://127.0.0.1:8000/"
USERNAME = config.get(CFG_SECTION, "username")
PASSWORD = config.get(CFG_SECTION, "password")
AMULE_PASSWORD = config.get(CFG_SECTION, "amule_password")
XUNLEI_COMMAND = config.get(CFG_SECTION, "xunlei_command")
WGET_LOG = config.get(CFG_SECTION, "wget_log")

mkdir_p(os.path.dirname(WGET_LOG))
useXunLei = XUNLEI_COMMAND != None and len(XUNLEI_COMMAND) != 0
logger = logging.getLogger('piload')
hdlr = logging.FileHandler(expanduser('~/piload_client.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.ERROR)

def getToken():
    logger.info("getToken")
    url = SERVER + "api-token-auth/"
    params = urllib.urlencode({
            'username': USERNAME,
            'password': PASSWORD
    })
    data = json.load(urllib2.urlopen(url, params, TIMEOUT))
    logger.info(data)
    return data.get('token')

def getNewTask():
    logger.info("getNewTask")
    url = SERVER + "api/task/?format=json&status=N"
    req = urllib2.Request(url)
    req.add_header("Authorization", "Token " + TOKEN)
    try:
        tasks = json.load(urllib2.urlopen(req, None, TIMEOUT))
        return tasks
    except urllib2.URLError, e:
        logger.error(e)
        return []
    except urllib2.HTTPError, e:
        logger.error(e)
        return []
    except socket.timeout, e:
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
            resp = urllib2.urlopen(req, timeout=TIMEOUT)
            logger.info(resp)
        except urllib2.URLError, e:
            logger.error(e)
        except urllib2.HTTPError, e:
            logger.error(e)
        except socket.timeout, e:
            logger.error(e)

def uploadStatus(status, downloads):
    logger.info("uploadStatus")
    url = SERVER + "update"
    params = urllib.urlencode({
            'username': USERNAME,
            'password': PASSWORD,
            'status': status,
            'downloads': downloads
    })
    try:
        resp = urllib2.urlopen(url, params, TIMEOUT)
        logger.info(resp)
    except urllib2.URLError, e:
        logger.error(e)
    except urllib2.HTTPError, e:
        logger.error(e)
    except socket.timeout, e:
        logger.error(e)

def getStatsLine(input):
    stats = ""
    for m in STATS_LINE_PATTERN.finditer(input):
        stats += m.group(0)
    stats += " "
    return stats

def getMuleStatus():
    logger.info("getMuleStatus")
    ret = ""
    if not cmd_exists('amulecmd'):
        return ret
    try:
        status = subprocess.check_output(["amulecmd", "-P", AMULE_PASSWORD, "-c", "status"])
        ret = getStatsLine(status)
    except subprocess.CalledProcessError, e:
        logger.error(e)
    
    return ret

def getMuleDownload():
    logger.info("getMuleDownload")
    ret = ""
    if not cmd_exists('amulecmd'):
        return ret
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

def xunleiLixianDownload(link):
    ret = subprocess.Popen([XUNLEI_COMMAND, "download", link])
    logger.info(ret)

def run():
    tasks = getNewTask();
    for t in tasks:
        uri = t.get("uri")
        logger.info(uri)
        if not useXunLei:
            addDownload(uri)
        else:
            xunleiLixianDownload(uri)
        setTaskRunning(t)

    progress = parseWgetLog(WGET_LOG)
    logger.info(progress)
    
    uploadStatus(getMuleStatus(), getMuleDownload())

TOKEN = getToken()
while True:
    try:
        logger.info("run")
        run()
        time.sleep(INTERVAL)
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(exc_type)
        logger.error(str(e))
        raise

