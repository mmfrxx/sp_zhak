from datetime import date, timedelta

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication \
    import JWTAuthentication

from authentication.models import User
from authentication.serializers import UserSerializer
from .models import Project, \
    ProjectAndUser, Event, GithubEvent, SlackEvent, TelegramEvent
from .serializers import ProjectSerializer, \
    GitHubEventSerializer, SlackEventSerializer
from .utils import serialize_events


# from .factory2 import slackFactory, gitFactory, tgFactory


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
            ProjectAndUser.objects.create(user=user, project=proj)
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
                project = Project.objects.filter(pk=project_pk).first()
                if project and project.team_lead == None:
                    if User.objects.filter(username=request.data.get('username')).exists():
                        team_lead = User.objects.get(username=request.data.get('username'))
                        project.team_lead = team_lead
                        project.save()
                        if not ProjectAndUser.objects.filter(user=team_lead, project=project).exists():
                            ProjectAndUser.objects.create(user=team_lead, project=project)
                        return Response("Success", HTTP_200_OK)
                return Response("Team lead for this project already exists or project does not exist.",
                                HTTP_400_BAD_REQUEST)
            return Response("Project is required.", HTTP_400_BAD_REQUEST)
        return Response("You are not allowed to do this.", HTTP_400_BAD_REQUEST)


class Delete_team_lead(APIView):
    def delete(self, request):
        user = request.user
        if (user.is_manager or user.is_organizationOwner or user.is_admin) and user.is_active:
            project_pk = request.data.get('pk')
            if project_pk:
                project = Project.objects.filter(pk=project_pk).first()
                if project and project.team_lead is not None:
                    project.team_lead = None
                    project.save()
                    return Response("Success", HTTP_200_OK)
                return Response("Team lead for this project is not set or project does not exist.",
                                HTTP_400_BAD_REQUEST)
            return Response("Project is required.", HTTP_400_BAD_REQUEST)
        return Response("You are not allowed to do this.", HTTP_400_BAD_REQUEST)

        pass


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
                    if not ProjectAndUser.objects.filter(user__username=user_to_add.username,
                                                         project_id=project.id).exists():
                        ProjectAndUser.objects.create(user=user_to_add, project=project)
                        return Response("Success", HTTP_200_OK)
                    return Response("User already in project.", HTTP_400_BAD_REQUEST)
                return Response("User does not exist.", HTTP_400_BAD_REQUEST)
            return Response("You are not allowed to do this.", HTTP_400_BAD_REQUEST)
        return Response("Project is required.", HTTP_400_BAD_REQUEST)


class Remove_team_member(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    def delete(self, request):
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
                        if user_to_remove == project.team_lead:
                            project.team_lead = None
                            project.save()
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
            requested_user = User.objects.filter(pk=pk).first()
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


class ReducePoints(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user = request.user
        username = request.data.get('username')
        points = request.data.get('points')
        project_pk = request.data.get('pk')
        if project_pk:
            project = Project.objects.get(pk=project_pk)
            if (
                    user.is_manager or user.is_organizationOwner or user.is_admin or user.id == project.team_lead.id) and user.is_active:
                student = User.objects.filter(username=username).first()
                if student:
                    student.account_bonus -= min(student.account_bonus, points)
                    student.save()
                    return Response(data=UserSerializer(student).data, status=HTTP_200_OK)
                return Response("No such user", HTTP_400_BAD_REQUEST)
            return Response("Access is denied", HTTP_400_BAD_REQUEST)
        return Response("No project pk", HTTP_400_BAD_REQUEST)


# request: user
# args: pk
class DeleteProjectView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    def delete(self, request, *args, **kwargs):
        user = request.user
        project_pk = kwargs.get("pk")
        if project_pk:
            project = Project.objects.get(pk=project_pk)
            if (
                    user.is_manager or user.is_organizationOwner or user.is_admin or user.id == project.team_lead.id) and user.is_active:
                project.delete()
                return Response("Success", HTTP_200_OK)
            return Response("You are not allowed to do this.", HTTP_400_BAD_REQUEST)
        return Response('Project does not exist', HTTP_400_BAD_REQUEST)


# requesting user must be in the project,
# i sort events by datetime descending
# if found in telegram events, send to tg serializer
# events should show: project name, type of event, message, user, bonus, time


class GetProjectEvents(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, pk):
        user = request.user
        project = Project.objects.filter(pk=pk).first()

        if project:
            if ProjectAndUser.objects.filter(user=user,
                                             project=project).exists() or user.is_manager or user.is_organizationOwner or user.is_admin:
                number_of_events = request.GET.get('limit', 0)
                events = Event.objects.filter(project=project).order_by('-timestamp').select_subclasses()
                if number_of_events:
                    events = Event.objects.filter(project=project).order_by('-timestamp').select_subclasses()[
                             :int(number_of_events)]
                return serialize_events(events)
            return Response('User not in project', HTTP_400_BAD_REQUEST)
        return Response('Project does not exist', HTTP_400_BAD_REQUEST)


class GetUserEvents(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, pk):
        requested_user = User.objects.filter(pk=pk).first()
        user = request.user
        if user.is_manager or user.is_organizationOwner or user.is_admin or requested_user == user:
            number_of_events = request.GET.get('limit', 0)
            events = Event.objects.filter(user=requested_user).order_by('-timestamp').select_subclasses()
            if number_of_events:
                events = Event.objects.filter(user=requested_user).order_by('-timestamp').select_subclasses()[
                         :int(number_of_events)]
            return serialize_events(events)
        return Response('You are not allowed to do this', HTTP_400_BAD_REQUEST)


# the user that is being changed should be the same user who wants to change info
# data to be changed:
class PostUserInfo(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserSerializer

    def check_user(self, user):
        username = user.get('username', None)
        first_name = user.get('first_name', None)
        last_name = user.get('last_name', None)

        if username and not username.isalnum():
            return (True,
                    'The username should contain only alphanumeric characters')
        if (first_name and not first_name.isalpha()) \
                or (last_name and not last_name.isalpha()):
            return (True,
                    'The first or last name should contain only alphabetic characters')
        if username and User.objects.filter(username=username).exists():
            return (True,
                    'Username is already in use')
        if not username and not first_name and not last_name:
            return (True,
                    'Nothing to change')
        return (False, '')

    def post(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")
        if user.is_active:
            requested_user = User.objects.filter(pk=pk).first()
            if user == requested_user or user.is_admin:
                check = self.check_user(request.data)
                if not check[0]:
                    serializer = self.serializer_class(requested_user,
                                                       data=request.data,
                                                       partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, HTTP_200_OK)
                return Response(check[1], HTTP_400_BAD_REQUEST)
            return Response('Permission denied', HTTP_400_BAD_REQUEST)
        return Response('User not active', HTTP_400_BAD_REQUEST)


# time frame: 1 week, 2 weeks, 1 month, 3 month, 6 months, 12 months, all time
class GetStatistics(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserSerializer
    project = -1

    def get(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")
        project = Project.objects.filter(pk=pk).first()
        time_frame = request.GET.get('time_frame', '1_week')
        if ProjectAndUser.objects.filter(user=user,
                                         project=project).exists() or user.is_manager or user.is_organizationOwner or user.is_admin:
            if project:
                self.project = project
                number_of_days = 7  # how many units in x axis
                divisions = 7
                print(time_frame)
                if time_frame != '1_week':
                    divisions = 14
                    if time_frame == '2_weeks':
                        number_of_days = 14
                    elif time_frame == '1_month':
                        number_of_days = 30
                    elif time_frame == '3_months':
                        number_of_days = 90
                    elif time_frame == '6_months':
                        number_of_days = 180
                    elif time_frame == '12_months':
                        number_of_days = 365
                project_users = ProjectAndUser.objects.all().filter(project=project)
                data = {}

                for item in project_users:
                    user_events = self.getData(item.user, number_of_days, divisions)
                    data[item.user.username] = user_events
                return Response(data, HTTP_200_OK)
            return Response('No project found', HTTP_400_BAD_REQUEST)
        return Response('Permission denied', HTTP_400_BAD_REQUEST)

    def getData(self, user, number_of_days, number_of_divisions):
        increments = number_of_days / number_of_divisions  # 365/14
        start_day = date.today() - timedelta(days=number_of_days)  # now - 365 days
        data = {"Slack": {}, "Telegram": {}, "Git": {}}
        while (start_day <= (date.today())):
            end_day = start_day + timedelta(days=increments)  # this day last year + 26 days
            # make query Event.objects.all.get_subclasses(from start day; to end day, user= user, project = project)
            # and then save it in dict

            slack_events = Event.objects.filter(project=self.project, user=user, timestamp__gte=start_day,
                                                timestamp__lt=end_day).select_subclasses(SlackEvent)
            data["Slack"][str(start_day) + " - " + str(end_day)] = len(SlackEventSerializer(slack_events, many=True).data)

            github_events = Event.objects.filter(project=self.project, user=user, timestamp__gte=start_day,
                                                 timestamp__lt=end_day).select_subclasses(
                GithubEvent)
            data["Git"][str(start_day) + " - " + str(end_day)] = len(GitHubEventSerializer(github_events, many=True).data)

            tg_events = Event.objects.filter(project=self.project, user=user, timestamp__gte=start_day,
                                             timestamp__lt=end_day).select_subclasses(
                TelegramEvent)
            data["Telegram"][str(start_day) + " - " + str(end_day)] = len(GitHubEventSerializer(tg_events, many=True).data)

            # start_day = end_day + timedelta(days=1)
            start_day = end_day

        return data
