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
# bind github account

# recieve authentication token and exchange to oauth token
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
# repo url $username/repo_name
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
        response = requests.post('https://api.github.com/repos/' + repo + '/hooks', headers=headers, data=data)
        # save project and project repository name
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
# +bonuses
class PostEvent(APIView):
    def post(self, request, *args, **kwargs):
        event = dict(request.data)
        type = request.headers['X-GitHub-Event']
        github_repo = event['repository']['id']
        print(type)
        github = GithubAndProject.objects.filter(github_repo_id=github_repo).first()
        if github:
            project = github.project
            if type == 'push':
                self.process_push_event(event, type, project)
            elif type == 'pull_request':
                self.process_pr_event(event, type, project)
            return Response(HTTP_200_OK)
        return Response("could not find any matching repository for the project", HTTP_400_BAD_REQUEST)

    # there can be multiple commits in one push: one commit -> one github_event
    def process_push_event(self, event, type, project ):
        github_repo_name = event['repository']['name']
        commit_owner = event['pusher']['name']
        github_account = GithubAndUser.objects.filter(login=commit_owner).first()
        user = github_account.user
        for i in range(len(event['commits'])):
            metadata = {
                "modified_data": event['commits'][i]['modified'],
                "message": event['commits'][i]['message'],
                "link_to_commit": event['commits'][i]['url'],
            }
            GithubEvent.objects.create(project=project, user=user, type=type, repo=github_repo_name, metaData=metadata)
        self.assign_bonuses(user, project)

    def assign_bonuses(self, user, project):
        user.account_bonus = user.account_bonus+project.git_bonus
        user.save()

    #pull-requests
    def process_pr_event(self, event, type, project):
        github_repo_name = event['repository']['name']
        pr_owner = event['pull_request']['user']['login']
        github_account = GithubAndUser.objects.filter(login=pr_owner).first()
        user = github_account.user
        metadata = {
            "pr_action": event['action'],
            "message": event['pull_request']['body'],
            "link_to_pr": event['pull_request']['url'],
        }
        GithubEvent.objects.create(project=project, user=user, type=type, repo=github_repo_name, metaData=metadata)
        self.assign_bonuses(user, project)


