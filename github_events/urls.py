from django.urls import path, re_path
from .views import *
urlpatterns = [
    path('events', PostEvent.as_view(), name='events'),


    ]