from django.contrib import admin
from piload.models import Task, Status, Download
from django.contrib.auth.models import Permission

admin.site.register(Permission)

admin.site.register(Task)
admin.site.register(Status)
admin.site.register(Download)