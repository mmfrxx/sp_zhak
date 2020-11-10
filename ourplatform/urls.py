from django.urls import path
from .views import *

urlpatterns = [
    path('create_project', ProjectView.as_view(), name='create_project'),
    path('set_team_lead', Add_team_lead.as_view(), name='set_team_lead'),
    path('add_team_member', Add_team_member.as_view(), name='add_team_member'),
    path('remove_team_member', Remove_team_member.as_view(), name='remove_team_member'),
    path('get-user-info/<int:pk>', GetUserInfoView.as_view()),
    path('get-projects-for-user/<int:pk>', GetProjectsForUserView.as_view()),
    path('get-users-of-project/<int:pk>', GetUsersOfProjectView.as_view()),
    path('get-project-activities/<int:pk>/<int:limit>', GetProjectEvents.as_view(), name='get_project_events'),
    path('get-project-activities/<int:pk>', GetProjectEvents.as_view(), name='get_project_events'),


    path('change-user-information/<int:pk>', PostUserInfo.as_view(), name='get_project_events'),
    path('delete-project/<int:pk>', DeleteProjectView.as_view(), name='delete-project' ),

]