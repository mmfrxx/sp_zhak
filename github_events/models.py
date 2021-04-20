from django.db import models
from authentication.models import User
from ourplatform.models import Project
# Create your models here.

class GithubAndProject(models.Model):
    github_repo_id = models.CharField(max_length=255, db_index=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, unique=True)
    github_repo_name = models.CharField(max_length=255, default="github repo")
    webhook_id = models.CharField(max_length=255, null = False)
    repo_owner = models.CharField(max_length=255, null = False)

class GithubAndUser(models.Model):
    login = models.CharField(max_length=255, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, null=False)
