from django.shortcuts import render
from rest_framework.views import APIView
from authentication.models import User
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from .serializers import ProjectSerializer
from .models import Project, ProjectAndUser
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication, JWTTokenUserAuthentication
from rest_framework.response import Response
from authentication.serializers import UserSerializer
from sp.permissions import IsActive, IsManagerOwnerAdminTeamLead

# Create your views here.

class ProjectView(APIView):
    authentication_classes = [JWTAuthentication]

    # permission_classes = [IsAuthenticated,]

    def post(self, request):
        user = request.user
        if (user.is_manager or user.is_organizationOwner or user.is_admin) and user.is_active:
            name = request.data.get('name')
            telegram_bonus = request.data.get('telegram_bonus')
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
            if (user.is_manager or user.is_organizationOwner or user.is_admin or user.id == project.team_lead.id) and user.is_active:
                if User.objects.filter(username=request.data.get('username')).exists():
                    user_to_add = User.objects.get(username=request.data.get('username'))
                    if not ProjectAndUser.objects.filter(user__username=user_to_add.username, project_id=project.id).exists():
                        ProjectAndUser.objects.create(user=user_to_add, project=project)
                        return Response("Success", HTTP_200_OK)
                    return Response("User already in project.", HTTP_400_BAD_REQUEST)
                return Response("User does not exist.", HTTP_400_BAD_REQUEST)
            return Response("You are not allowed to do this.", HTTP_400_BAD_REQUEST)
        return Response("Project is required.", HTTP_400_BAD_REQUEST)


# request: user, pk, username
class Remove_team_member(APIView):
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
                    user_to_remove = User.objects.get(username=request.data.get('username'))
                    if ProjectAndUser.objects.filter(user__username=user_to_remove.username,
                                                         project_id=project.id).exists():
                        ProjectAndUser.objects.get(user=user_to_remove, project=project).delete()
                        return Response("Success", HTTP_200_OK)
                    return Response("User not in project", HTTP_400_BAD_REQUEST)
                return Response("User does not exist.", HTTP_400_BAD_REQUEST)
            return Response("You are not allowed to do this.", HTTP_400_BAD_REQUEST)
        return Response("Project is required.", HTTP_400_BAD_REQUEST)

class GetUserInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")
        if user.is_active:
            requested_user = User.objects.filter(pk = pk).first()
            if requested_user:
                req_user_data = self.serializer_class(requested_user).data
                if not user.is_manager and not user.is_organizationOwner and not user.is_admin and user.username != requested_user.username:
                    req_user_data['account_bonus'] = 0
                return Response(data=req_user_data, status=HTTP_200_OK)
            return Response('User does not exist', HTTP_400_BAD_REQUEST)
        return Response('Please activate your account', HTTP_400_BAD_REQUEST)    

class GetProjectsForUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]
    serializer_class = ProjectSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")
        if user.is_active:
            requested_user = User.objects.filter(pk=pk).first()
            if requested_user:
                projects = [pr.project for pr in ProjectAndUser.objects.filter(user=requested_user)]
                projects_data = ProjectSerializer(projects, many=True).data
                return Response(projects_data, HTTP_200_OK)
            return Response('User does not exists', HTTP_400_BAD_REQUEST)
        return Response('Please activate your account', HTTP_400_BAD_REQUEST)  

class GetUsersOfProjectView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")
        project = Project.objects.filter(pk=pk).first()
        if project:
            users = [pr.user for pr in ProjectAndUser.objects.filter(project=project)]
            users = UserSerializer(users, many=True).data
            if not user.is_manager and not user.is_organizationOwner and not user.is_admin:
                for user in users:
                    user['account_bonus'] = 0
            return Response(users, HTTP_200_OK)
        return Response('Project does not exist', HTTP_400_BAD_REQUEST)

class  ReducePoints(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [ IsAuthenticated,]

    def post(self, request):
        user = request.user 
        username = request.data.get('username')
        points = request.data.get('points')
        project_pk = request.data.get('pk')
        if project_pk:
            project = Project.objects.get(pk=project_pk)
            if (user.is_manager or user.is_organizationOwner or user.is_admin or user.id == project.team_lead.id) and user.is_active:
                student = User.objects.filter(username=username).first()
                if student:
                    student.account_bonus -= min(student.account_bonus, points)
                    student.save()
                    return Response(data=UserSerializer(student).data, status=HTTP_200_OK)
                return Response("No such user", HTTP_400_BAD_REQUEST)
            return Response("Access is denied", HTTP_400_BAD_REQUEST)
        return Response("No project pk", HTTP_400_BAD_REQUEST)





        






