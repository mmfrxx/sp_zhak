from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from authentication.models import User
from rest_framework.status import *
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication \
    import JWTAuthentication
from rest_framework.response import Response
import requests
import json
from .models import *
from ourplatform.models import GithubEvent, Project
from ourplatform.serializers import GitHubEventSerializer
import os

GITHUB_CLIENT_SECRET = getattr(settings, 'GITHUB_CLIENT_SECRET', None)
GITHUB_CLIENT_ID = getattr(settings, 'GITHUB_CLIENT_ID', None)
GITHUB_DEVELOPER_KEY = getattr(settings, 'GITHUB_DEVELOPER_KEY', None)


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
        user = request.user
        code = request.data.get('code')
        if code:
            token = self.exchange_code_to_token(code)
            login = self.get_account_login(token)
            GithubAndUser.objects.create(user=user, token=token, login=login)
            return Response("Successfully bound github account", HTTP_200_OK)
        return Response("code not found")

    def exchange_code_to_token(self, code):
        data = {"client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code
                }
        response = requests.post('https://github.com/login/oauth/access_token', params=data)
        if response.status_code == 200:
            token_info = response.content.decode()
            token = token_info.split("=")[1]
            token = token.split('&')[0]
            return token
        else:
            return Response("Error occured during authenticating", HTTP_400_BAD_REQUEST)

    def get_account_login(self, token):
        headers = {
            'Authorization': 'token ' + token,
        }
        response = requests.get('https://api.github.com/user', headers=headers)
        if response.status_code == 200:
            login = response.json()['login']
            return login
        else:
            return Response("Error occured during authorization", HTTP_400_BAD_REQUEST)


# bind to a repo
# repo url $username/repo_name
class CreateWebHook(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        repo = request.data.get('repo')
        user = request.user
        user_github_account = GithubAndUser.objects.filter(user=user).first()
        project_pk = kwargs.get("pk")
        project = Project.objects.filter(pk=project_pk).first()

        if not project:
            return Response("No such project found", HTTP_400_BAD_REQUEST)

        if not user_github_account:
            return Response("Authorize your github account", HTTP_400_BAD_REQUEST)
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': 'token ' + GITHUB_DEVELOPER_KEY,
        }
        data = {
            "config":
            {
                "url": "http://b5b192343036.ngrok.io/github/events",
                "content_type": "json"

            },
            "events": ["push", "pull_request"
                       ],
            "name": "web",
            "active": True
        }
        data = json.dumps(data)
        response = requests.post('https://api.github.com/repos/'+repo+'/hooks',
                                 headers=headers, data=data)
        if response.status_code == 201:
            github_repo_id= self.get_repo_id(user_github_account.token, repo)
            webhook_id = response.json()['id']
            repo_info = repo.split("/")
            GithubAndProject.objects.create(project=project, github_repo_name = repo_info[1], github_repo_id = github_repo_id, webhook_id = webhook_id, repo_owner = repo_info[0])
            return Response("Webhook successfully created", HTTP_200_OK)
        return Response(response.json()['message'], HTTP_400_BAD_REQUEST)

    def get_repo_id(self, token, repo):
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            "Authorization": "token " + token
        }
        response = requests.get('https://api.github.com/repos/' +repo, headers=headers)
        if response.status_code == 200:
            return response.json()['id']
        return Response("Could not retrieve id of the repo", HTTP_400_BAD_REQUEST)


# get repo event

class PostEvent(APIView):
    def post(self, request, *args, **kwargs):
        event = dict(request.data)
        type = request.headers['X-GitHub-Event']
        github_repo = event['repository']['id']
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
    def process_push_event(self, event, type, project):
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
        user.account_bonus = user.account_bonus + project.git_bonus
        user.save()

    # pull-requests
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



class DeleteHook(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]
    def delete(self, request, *args, **kwargs):
        project_pk = kwargs.get("pk")
        project = Project.objects.filter(pk=project_pk).first()
        if not project:
            return Response("No such project found", HTTP_400_BAD_REQUEST)
        github_webhook = GithubAndProject.objects.filter(project=project).first()
        owner = github_webhook.repo_owner
        webhook_id  = github_webhook.webhook_id
        repo_name = github_webhook.github_repo_name
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': 'token ' + GITHUB_DEVELOPER_KEY,
        }
        print(f'https://api.github.com/repos/{owner}/{repo_name}/hooks/{webhook_id}')
        response = requests.delete(f'https://api.github.com/repos/{owner}/{repo_name}/hooks/{webhook_id}',
                                 headers=headers)
        if response.status_code == 204:
            github_webhook.delete()
            return Response( HTTP_204_NO_CONTENT)
        return Response("Webhook was not removed", HTTP_400_BAD_REQUEST)

class UnbindGithubAccount(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]
    def delete(self,request, *args, **kwargs):
        user = request.user
        user_github_account = GithubAndUser.objects.filter(user=user).first()
        if user_github_account:
            user_github_account.delete()
            return Response(HTTP_204_NO_CONTENT)
        return Response("No github account associated with the account")

