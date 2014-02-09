from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, logout
from django.utils import timezone
from rest_framework import viewsets
from datetime import datetime
import logging
import re
import django_filters
import urllib
import redis

from piload.serializers import TaskSerializer, StatusSerializer, DownloadSerializer
from piload.models import Task, Status, Download
from piload.utils import sizeof_fmt, elapsed_time


ED2K_SCHEME = "^ed2k\:\/\/"
ED2K_FILE = "\|file"
#ED2K_NAME = "\|(?P<name>(([A-Za-z0-9 \-\_\.])|(\%[A-Fa-f0-9]{2}))+)"
ED2K_NAME = "\|(?P<name>[^\|]+)"
ED2K_SIZE = "\|(?P<size>[0-9]+)"
ED2K_FILE_HASH = "\|[A-Fa-f0-9]{32}"
ED2K_ROOT_HASH = "(\|h=[A-Za-z0-9]{32})?"
ED2K_END = "\|\/$"

ED2K_URI = ED2K_SCHEME + ED2K_FILE + ED2K_NAME + ED2K_SIZE + ED2K_FILE_HASH + ED2K_ROOT_HASH + ED2K_END
ED2K_PATTERN = re.compile(ED2K_URI)

#REGEX_DOWNLOAD = " > [A-Fa-f0-9]{32} (?P<name>\S+)\\n\S+\\n"
REGEX_DOWNLOAD = " > [A-Fa-f0-9]{32} (?P<name>.+)\\n >(?P<stats>.+)\\n"
DOWNLOAD_PATTERN = re.compile(REGEX_DOWNLOAD)

RedisDB = redis.StrictRedis(host="localhost", port="6379", db=0)

class TaskFilter(django_filters.FilterSet):
    class Meta:
        model = Task
        fields = ['status']

class TaskViewSet(viewsets.ModelViewSet):
    model = Task
    serializer_class = TaskSerializer
    filter_class = TaskFilter

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(user=user) 

class StatusViewSet(viewsets.ModelViewSet):
    model = Status
    serializer_class = StatusSerializer

    def get_queryset(self):
        user = self.request.user
        return Status.objects.filter(user=user)

class DownloadViewSet(viewsets.ModelViewSet):
    model = Download
    serializer_class = DownloadSerializer

    def get_queryset(self):
        user = self.request.user
        return Download.objects.filter(user=user)

def add_task_view(request):
    if not request.user.is_authenticated():
        return redirect('/api-auth/login/?next=%s' % request.path)
    u = request.user
    try:
        update_date = "unknown"
        status_list = []
        wait_list = []
        download_list = []
        now = timezone.now();

        waiting = Task.objects.filter(user=u, status='N')
        for w in waiting:
            m = ED2K_PATTERN.search(w.uri)
            elapse = now - w.add_date
            wait_list.append({
                "name":urllib.unquote(m.group("name").encode('ASCII')),
                "size":sizeof_fmt(int(m.group("size"))),
                "uri":urllib.unquote(w.uri.encode('ASCII')),
                "add_date":elapsed_time(elapse.total_seconds()),
                })

        downloads = RedisDB.get("download-%d" % u.id)
        if downloads:
            for m in DOWNLOAD_PATTERN.finditer(downloads):
                download_list.append({
                    "name":m.group("name"),
                    "stats":m.group("stats"),
                })

        status = RedisDB.get("status-%d" % u.id)
        if status:
            status_list = status.splitlines()
        update_date = RedisDB.get("timestamp-%d" % u.id)

        c = RequestContext(request, {
            "user_name": u.username,
            "update_date": update_date,
            "status_list": status_list,
            "wait_list": wait_list,
            "download_list":download_list,
        })
    except Status.DoesNotExist:
        c = RequestContext(request, {
            "user_name": u.username,
            "update_date": "unknown",
        })
    return render(request, "piload/addtask.html", c)

def submit_task_view(request):
    uri = request.POST['link']
    isEd2k = ED2K_PATTERN.match(uri)
    if not isEd2k:
        return HttpResponseRedirect(reverse("add_task_view"))
    else:
        u = request.user
        t = Task(user=u)
        t.uri = uri
        t.save();
        return HttpResponseRedirect(reverse("add_task_view"))

@csrf_exempt
def update_status_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        status = request.POST['status']
        downloads = request.POST['downloads']
        RedisDB.set("status-%d" % user.id, status)
        RedisDB.set("download-%d" % user.id, downloads)
        d = datetime.now()
        RedisDB.set("timestamp-%d" % user.id, str(d))
        return HttpResponse("ok")
    else:
        return HttpResponse("error")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("add_task_view"))
