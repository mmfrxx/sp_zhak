from django.shortcuts import render
from rest_framework.views import APIView
from authentication.models import User
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication \
    import JWTAuthentication
from secretsnotlib import GITHUB_CLIENT_SECRET, GITHUB_CLIENT_ID
from rest_framework.response import Response
import requests
import json
from .models import *
from ourplatform.models import GithubEvent
from ourplatform.serializers import GitHubEventSerializer
import os


class GithubPage(APIView):
    def get(self, request):
        return render(request, 'index.html', {})


# Create your views here.

# recieve authentication token and exchange to oauth token
# Frontend button directs to https://github.com/login/oauth/authorize?client_id=01bd74491b2142e0a049
# and it redirects to frontend and from frontend I get a request with code in payload
class GithubAuth(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        # recieve token
        user = request.user
        code = request.data.get('code')
        # code = str(request.build_absolute_uri()).split("code=")[1]
        if not code:
            return Response("Authorization failed", HTTP_400_BAD_REQUEST)
        # exhcange temperary code to oauth token
        token = self.exchange_code_to_token(code)
        # get account info
        login = self.get_account_login(token)

        # save user info to db
        GithubAndUser.objects.create(user=user, token=token, login=login)
        return Response("Successfully bound github account", HTTP_200_OK)

    def exchange_code_to_token(self, code):
        data = {"client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code
                }
        response = requests.post('https://github.com/login/oauth/access_token', params=data)
        token_info = response.content.decode()
        return token_info

    def get_account_login(self, token):
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            "Authorization": "token " + token
        }
        response = requests.post('https://api.github.com/user', headers=headers)
        login = response.json()['login']
        return login

# bind to a repo
#repo url $username/repo_name
class CreateWebHook(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    #  serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        repo = request.data.get('repo')
        user = request.user
        user_github_account = GithubAndUser.objects.filter(user=user).first()

        if not user_github_account:
            return Response("Authorize your github account", HTTP_400_BAD_REQUEST)
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            "Authorization": "token " + user_github_account.token
        }
        data = {"config":
                    {"url": "http://fa4fc41e6321.ngrok.io/github/events"
                     }
                }
        data = json.dumps(data)
        response = requests.post('https://api.github.com/repos/'+repo+'/hooks', headers=headers, data=data)
        #save project and project repository name
        project_pk = kwargs.get("pk")
        project = Project.objects.filter(pk=project_pk).first()
        GithubAndProject(project=project, github_repo_name=repo)
        return Response(response.json(), HTTP_200_OK)
    def get_repo_id(self, token):
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            "Authorization": "token " + token
        }

        response = requests.post('https://api.github.com/repos/' + repo + '/hooks', headers=headers, data=data)


# get repo event
#+bonuses
class PostEvent(APIView):
    def post(self, request, *args, **kwargs):
        event = dict(request.data)
        github_repo = event['repository']['id']
        github = GithubAndProject.objects.filter(github_repo_id = github_repo).first()
        project = github.project
        owner = event['repository']['owner']['login']
        github_account = GithubAndUser.objects.filter(login = owner)
        user = github_account.user
        #type
        #repo
        #metaData
        GithubEvent.objects.create(project=project, user=user, type=type)
        return Response(HTTP_200_OK)
