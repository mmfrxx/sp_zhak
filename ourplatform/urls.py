from django.urls import path
from .views import *

urlpatterns = [
    path('create_project', ProjectView.as_view(), name='create_project'),
    path('set_team_lead', Add_team_lead.as_view(), name='set_team_lead'),
]