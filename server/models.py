from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Task(models.Model):
    STATUS = (
        ("N", "New"),
        ("R", "Running"),
        ("F", "Finished"),
        ("D", "Deleted"),
    )
    user =  models.ForeignKey(User)
    uri = models.CharField(max_length=10000)
    add_date = models.DateTimeField("date added", auto_now=True)
    status = models.CharField(max_length=1, choices=STATUS, default="N")
    def __unicode__(self):
        return self.uri + " " + self.status

class Status(models.Model):
    user = models.ForeignKey(User)
    update_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10000)
    def __unicode__(self):
        return str(self.update_date) + " " + self.status

class Download(models.Model):
    user = models.ForeignKey(User)
    update_date = models.DateTimeField(auto_now=True)
    downloads = models.CharField(max_length=10000)
    def __unicode__(self):
        return str(self.update_date) + " " + self.downloads