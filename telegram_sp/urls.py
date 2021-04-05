from django.urls import path
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('events', csrf_exempt(Events.as_view())),
    path('bind_group_platform/<int:pk>', GroupBindPlatform.as_view()),
    path('bind_profile_platform', TelegramProfilePlatform.as_view())
]