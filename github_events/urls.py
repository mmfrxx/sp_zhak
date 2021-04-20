from django.urls import path, re_path
from .views import *
urlpatterns = [
    path('events', PostEvent.as_view(), name='events'),
    path('', GithubPage.as_view()),
    path('code', GithubAuth.as_view()),
    path('connect_to_repo/<int:pk>', CreateWebHook.as_view()),
    path('remove_webhook/<int:pk>', DeleteHook.as_view()),
    path('unbind_github_account',UnbindGithubAccount.as_view() )
    ]