from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from slack_sdk import WebClient
import uuid
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication \
    import JWTAuthentication

from authentication.models import User
from ourplatform.models import ProjectAndUser, Project, SlackEvent
from slackevents_sp.models import ChannelProject, ChannelCode, SlackProfileCode, SlackProfile

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)
client = WebClient(token=SLACK_BOT_USER_TOKEN)

text_channel = "Please, use this code {code} to bind this channel with your project"
text_profile = "Please, use this code {code} to bind your slack account with your profile"


class Events(APIView):
    @staticmethod
    def post(request, *args, **kwargs):
        slack_message = request.data
        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message,
                            status=status.HTTP_200_OK)

        if 'event' in slack_message:
            event_message = slack_message.get('event')
            if event_message.get('subtype') == 'bot_message':
                return Response(status=status.HTTP_200_OK)
            if 'bot_id' not in event_message:
                if 'channel' == event_message.get('channel_type'):
                    channel_id = event_message.get('channel')
                    user_id = event_message.get('user')
                    channel_proj = ChannelProject.objects.filter(channel_id=channel_id)
                    profile_account = SlackProfile.objects.filter(profile_id=user_id)
                    if channel_proj.first() is None or profile_account.first() is None:
                        return Response(status=status.HTTP_200_OK)
                    user = profile_account.first().user
                    project = channel_proj.first().project
                    user.account_bonus += project.slack_bonus
                    user.save()
                SlackEvent.objects.create(project=channel_proj.first().project,
                                              user=profile_account.first().user,
                                              message=event_message.get('text'),
                                              channel=channel_proj.first().channel_name)
        return Response(status=status.HTTP_200_OK)


class Channel(APIView):
    @staticmethod
    def post(request, *args, **kwargs):
        slack_message = request.data
        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if 'bot_profile' not in slack_message:
            if "directmessage" == slack_message.get('channel_name'):
                client.chat_postMessage(channel=slack_message.get('channel_id'),
                                        text="\\bind_channel command can be used only in channels")
            else:
                if ChannelProject.objects.filter(channel_id=slack_message.get('channel_id')).first() is None:
                    code = uuid.uuid4()
                    ChannelCode.objects.create(channel_id=slack_message.get('channel_id'),
                                               code=code,
                                               channel_name=slack_message.get('channel_name'))
                    client.chat_postMessage(channel=slack_message.get('channel_id'),
                                            text=text_channel.format(code=code))
                else:
                    client.chat_postMessage(channel=slack_message.get('channel_id'),
                                            text="This channel is already bound with a project")
        return Response(status=status.HTTP_200_OK)


class ChannelBindPlatform(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def post(request, *args, **kwargs):
        user = request.user
        code = request.data.get('code')
        project_id = kwargs.get("pk")
        project = Project.objects.filter(pk=project_id).first()
        channel_code = ChannelCode.objects.filter(code=code)
        if channel_code.first() is None:
            return Response("Please, use valid code", status=status.HTTP_412_PRECONDITION_FAILED)
        channel_id = channel_code.first().channel_id
        channel_name = channel_code.first().channel_name
        if ChannelProject.objects.filter(channel_id=channel_id).first() is not None \
                or ChannelProject.objects.filter(project=project).first() is not None:
            return Response("Channel or Project is already bound", status=status.HTTP_403_FORBIDDEN)
        if ProjectAndUser.objects.filter(project=project, user=user).first() is None:
            return Response("You are not member of this project", status=status.HTTP_403_FORBIDDEN)
        ChannelProject.objects.create(channel_id=channel_id, project_id=project_id, channel_name=channel_name)
        channel_code.delete()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, *args, **kwargs):
        user = request.user
        project_id = kwargs.get("pk")
        project = Project.objects.filter(pk=project_id).first()
        if ProjectAndUser.objects.filter(project=project, user=user).first() is None:
            return Response("You are not member of this project", status=status.HTTP_403_FORBIDDEN)
        if ChannelProject.objects.filter(project=project).first() is None:
            return Response("Project is not bound")
        ChannelProject.objects.filter(project=project).delete()
        return Response(status=status.HTTP_200_OK)


class SlackProfileBind(APIView):
    @staticmethod
    def post(request, *args, **kwargs):
        slack_message = request.data
        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if 'bot_profile' not in slack_message:
            if "directmessage" != slack_message.get('channel_name'):
                client.chat_postMessage(channel=slack_message.get('channel_id'),
                                        text="\\bind_profile command can be used only in direct message")
            else:
                if SlackProfile.objects.filter(profile_id=slack_message.get('user_id')).first() is None:
                    code = uuid.uuid4()
                    SlackProfileCode.objects.create(profile_id=slack_message.get('user_id'),
                                                    code=code,
                                                    profile_name=slack_message.get('user_name'))
                    client.chat_postMessage(channel=slack_message.get('channel_id'),
                                            text=text_profile.format(code=code))
                else:
                    client.chat_postMessage(channel=slack_message.get('channel_id'),
                                            text="This profile is already bound with an account")
            return Response(status=status.HTTP_200_OK)


class SlackProfilePlatform(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def post(request, *args, **kwargs):
        user = request.user
        code = request.data.get('code')
        profile_code = SlackProfileCode.objects.filter(code=code)
        if profile_code.first() is None:
            return Response("Please, use valid code", status=status.HTTP_412_PRECONDITION_FAILED)
        profile_id = profile_code.first().profile_id
        if SlackProfile.objects.filter(profile_id=profile_id).first() is not None \
                or SlackProfile.objects.filter(user=user).first() is not None:
            return Response("Account or profile is already bound", status=status.HTTP_403_FORBIDDEN)
        SlackProfile.objects.create(profile_id=profile_id, user=user, profile_name=profile_code.first().profile_name)
        profile_code.delete()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, *args, **kwargs):
        user = request.user

        if SlackProfile.objects.filter(user=user).first() is None:
            return Response("Account is not bound")
        SlackProfile.objects.filter(user=user).delete()
        return Response(status=status.HTTP_200_OK)
