from django.db import models
from authentication.models import User
from ourplatform.models import Project


class ChannelProject(models.Model):
    channel_id = models.CharField(max_length=255, db_index=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=255, default="Slack channel")


class ChannelCode(models.Model):
    channel_id = models.CharField(max_length=255)
    channel_name = models.CharField(max_length=255, default="Slack channel")
    code = models.CharField(max_length=255)


class SlackProfileCode(models.Model):
    profile_id = models.CharField(max_length=255)
    profile_name = models.CharField(max_length=255, default="Slack profile")
    code = models.CharField(max_length=255)


class SlackProfile(models.Model):
    profile_id = models.CharField(max_length=255, db_index=True)
    profile_name = models.CharField(max_length=255, default="Slack profile")
    user = models.ForeignKey(User, on_delete=models.CASCADE)