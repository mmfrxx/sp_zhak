from django.urls import path
from .views import *


urlpatterns = [
    path('events', Events.as_view()),
    path('bind_channel', Channel.as_view()),
    path('bind_channel_platform/<int:pk>', ChannelBindPlatform.as_view()),
    path('bind_profile', SlackProfileBind.as_view()),
    path('bind_profile_platform', SlackProfilePlatform.as_view())
]