from django.db import models
from authentication.models import User


# Create your models here.
class Project(models.Model):
    team_lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255, db_index=True)
    telegram_bonus = models.IntegerField(default=50)
    slack_bonus = models.IntegerField(default=50)
    git_bonus = models.IntegerField(default=50)
    users = models.ManyToManyField(User,
                                   related_name="%(app_label)s_%(class)s_related",
                                   related_query_name="%(app_label)s_%(class)ss", )

class ProjectAndUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
