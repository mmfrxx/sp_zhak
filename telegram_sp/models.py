from django.db import models
from authentication.models import User
from ourplatform.models import Project


class GroupProject(models.Model):
    group_id = models.CharField(max_length=255, db_index=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=255, default="Telegram group")


class GroupCode(models.Model):
    group_id = models.CharField(max_length=255)
    group_name = models.CharField(max_length=255, default="Telegram group")
    code = models.CharField(max_length=255)


class TelegramProfileCode(models.Model):
    profile_id = models.CharField(max_length=255)
    profile_name = models.CharField(max_length=255, default="Telegram profile")
    code = models.CharField(max_length=255)


class TelegramProfile(models.Model):
    profile_id = models.CharField(max_length=255, db_index=True)
    profile_name = models.CharField(max_length=255, default="Slack profile")
    user = models.ForeignKey(User, on_delete=models.CASCADE)