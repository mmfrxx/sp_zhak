from django.urls import path, re_path
from .views import *


urlpatterns = [
    path('create_project', ProjectView.as_view(), name='create_project'),
    path('set_team_lead', Add_team_lead.as_view(), name='set_team_lead'),
    path('delete_team_lead', Delete_team_lead.as_view()),
    path('add_team_member', Add_team_member.as_view(), name='add_team_member'),
    path('remove_team_member', Remove_team_member.as_view(), name='remove_team_member'),
    path('get-user-info/<int:pk>', GetUserInfoView.as_view()),
    path('get-projects-for-user/<int:pk>', GetProjectsForUserView.as_view()),
    path('get-users-of-project/<int:pk>', GetUsersOfProjectView.as_view()),
    path('reduce-points', ReducePoints.as_view()),
    re_path(r'^get_project_activities/(?P<pk>[0-9]+)', GetProjectEvents.as_view(), name='get_project_events'),
    re_path(r'^get_user_activities/(?P<pk>\w+)+', GetUserEvents.as_view(), name='get_user_events'),
    path('change-user-information/<int:pk>', PostUserInfo.as_view(), name='get_project_events'),
    path('delete-project/<int:pk>', DeleteProjectView.as_view(), name='delete-project' ),
    path('get-statistics/<int:pk>', GetStatistics.as_view(), name='getStatistics'),
    # path('factory', makeEvents.as_view(), name='factory'),
]