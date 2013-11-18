from rest_framework import serializers
from piload.models import Task, Status, Download

class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "status", "uri", "add_date")

class StatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Status
        fields = ("id", "update_date", "status")

class DownloadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Download
        fields = ("id", "update_date", "downloads")