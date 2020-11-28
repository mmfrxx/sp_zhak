from django.db import models
from authentication.models import User
from model_utils.managers import InheritanceManager


# Create your models here.
class Project(models.Model):
    team_lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255, db_index=True)
    telegram_bonus = models.IntegerField(default=50)
    slack_bonus = models.IntegerField(default=50)
    git_bonus = models.IntegerField(default=50)
    project_description = models.TextField(null=True)
    project_team = models.CharField(max_length=255, null=True)


class ProjectAndUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Event(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_related",
                                related_query_name="%(app_label)s_%(class)ss", )
    user = models.ForeignKey(User, on_delete=models.CASCADE )
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = InheritanceManager()


class GithubEvent(Event):
    type = models.CharField(null=True, max_length=255)
    repo = models.CharField(null=True, max_length=255)
    metaData = models.CharField(null=True, max_length=255)


class SlackEvent(Event):
    message = models.TextField(null=True)
    channel = models.CharField(null=True, max_length=255)


class TelegramEvent(Event):
    message = models.CharField(max_length=255, default="")
    chat = models.CharField(null=True, max_length=255)
