from django.contrib import admin

# Register your models here.
from .models import GithubAndProject, GithubAndUser
# Register your models here.
admin.site.register(GithubAndProject)
admin.site.register(GithubAndUser)