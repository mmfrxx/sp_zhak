from django.shortcuts import render
from rest_framework.views import APIView
from authentication.models import User
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from .serializers import ProjectSerializer
from .models import Project, ProjectAndUser
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication, JWTTokenUserAuthentication
from rest_framework.response import Response


# Create your views here.

class ProjectView(APIView):
    authentication_classes = [JWTAuthentication]

    # permission_classes = [IsAuthenticated,]

    def post(self, request):
        user = request.user
        if (user.is_manager or user.is_organizationOwner or user.is_admin) and user.is_active:
            name = request.data.get('name')
            telegram_bonus = request.data.get('tg_bonus')
            slack_bonus = request.data.get('slack_bonus')
            git_bonus = request.data.get('git_bonus')

            if not name:
                return Response("The name of a project is required", HTTP_400_BAD_REQUEST)

            proj = Project(name=name)
            if telegram_bonus:
                proj.telegram_bonus = telegram_bonus
            if slack_bonus:
                proj.slack_bonus = slack_bonus
            if git_bonus:
                proj.git_bonus = git_bonus
            proj.save()
            serializer = ProjectSerializer(proj)
            return Response(serializer.data, HTTP_200_OK)
        else:
            return Response("You are not allowed to add projects.", HTTP_400_BAD_REQUEST)


class Add_team_lead(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user = request.user
        if (user.is_manager or user.is_organizationOwner or user.is_admin) and user.is_active:
            project_pk = request.data.get('pk')
            if project_pk:
                project = Project.objects.get(pk=project_pk)
                if project.team_lead == None:
                    if User.objects.filter(username=request.data.get('username')).exists():
                        team_lead = User.objects.get(username=request.data.get('username'))
                        project.team_lead = team_lead
                        project.save()
                        ProjectAndUser.objects.create(user=team_lead, project=project)
                        return Response("Success", HTTP_200_OK)
                else:
                    return Response("Team lead for this project already exists.", HTTP_400_BAD_REQUEST)
            return Response("Project is required.", HTTP_400_BAD_REQUEST)
        return Response("You are not allowed to do this.", HTTP_400_BAD_REQUEST)


# request: user, pk, username
class Add_team_member(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user = request.user
        project_pk = request.data.get('pk')
        if project_pk:
            project = Project.objects.get(pk=project_pk)
            if (
                    user.is_manager or user.is_organizationOwner or user.is_admin or user.id == project.team_lead.id) and user.is_active:
                if User.objects.filter(username=request.data.get('username')).exists():
                    user_to_add = User.objects.get(username=request.data.get('username'))
                    print(user_to_add.id)
                    print(user.id)
                    if Project.objects.filter(users__username=user_to_add.username).count() == 0:
                        project.users.add(user_to_add)
                        project.save()
                        return Response("Success", HTTP_200_OK)
                    return Response("Member already exists.", HTTP_400_BAD_REQUEST)
                return Response("User does not exist.", HTTP_400_BAD_REQUEST)
            return Response("You are not allowed to do this.", HTTP_400_BAD_REQUEST)
        return Response("Project is required.", HTTP_400_BAD_REQUEST)


