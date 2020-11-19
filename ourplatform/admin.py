from django.contrib import admin
from ourplatform.models import GithubEvent,TelegramEvent, SlackEvent, Project, ProjectAndUser
# Register your models here.
admin.site.register(GithubEvent)
admin.site.register(TelegramEvent)
admin.site.register(SlackEvent)
admin.site.register(Project)
admin.site.register(ProjectAndUser)