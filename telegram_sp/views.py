import json
import os
import uuid

import requests
from django.http import JsonResponse
from django.views import View
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from ourplatform.models import Project, ProjectAndUser, TelegramEvent
from telegram_sp.models import TelegramProfileCode, TelegramProfile, GroupCode, GroupProject

TG_URL = "https://api.telegram.org/bot"
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "error_token")
BIND_GROUP = "/bind_group"
BIND_PROFILE = "/bind_profile"


class Events(View):
    def post(self, request, *args, **kwargs):
        t_data = json.loads(request.body)
        t_message = t_data['message']
        if 'text' in t_message:
            text = t_message['text']
            t_chat = t_message['chat']
            group_type = t_chat['type']
            if 'entities' in t_message:
                if group_type == "private":
                    if BIND_GROUP in text:
                        msg = "Please use 'bind group' command only in group chats."
                        chat_id = t_chat['id']
                        self.send_message(msg, chat_id)
                    elif BIND_PROFILE in text:
                        self.bind_profile(t_data, t_chat['id'])
                elif group_type == "group":
                    if BIND_PROFILE in text:
                        msg = "Please use 'bind profile' command only in a private chat."
                        chat_id = t_chat['id']
                        self.send_message(msg, chat_id)
                    elif BIND_GROUP in text:
                        self.bind_group(t_data, t_chat['id'])
            else:
                self.process_telegram_events(t_data)
        return JsonResponse({"ok": "POST request processed"})

    @staticmethod
    def send_message(message, chat_id):
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        response = requests.post(
            f"{TG_URL}{TG_BOT_TOKEN}/sendMessage", data=data
        )

    def process_telegram_events(self, t_data):
        t_message = t_data['message']
        text = t_message['text']
        t_chat = t_message['chat']
        group_type = t_chat['type']
        if not t_message['from']['is_bot']:
            if 'group' == group_type:
                group_id = t_chat['id']
                user_id = t_message['from']['id']
                group_proj = GroupProject.objects.filter(group_id=group_id)
                profile_account = TelegramProfile.objects.filter(profile_id=user_id)
                if group_proj.first() is None or profile_account.first() is None:
                    return Response(status=status.HTTP_200_OK)
                user = profile_account.first().user
                project = group_proj.first().project
                user.account_bonus += project.telegram_bonus
                user.save()
                TelegramEvent.objects.create(project=group_proj.first().project,
                                             user=profile_account.first().user,
                                             message=text,
                                             chat=group_proj.first().group_name)

    def bind_profile(self, t_data, chat_id):
        t_message = t_data['message']
        if not t_message['from']['is_bot']:
            if TelegramProfile.objects.filter(profile_id=t_message['from']['id']).first() is None:
                code = uuid.uuid4()
                TelegramProfileCode.objects.create(profile_id=t_message['from']['id'],
                                                   code=code,
                                                   profile_name=t_message['from']['username'])
                self.send_message("Please, use this code {code} \
                to bind your telegram account with your profile".format(code=code), chat_id)
            else:
                self.send_message("This profile is already bound with an account", chat_id)

    def bind_group(self, t_data, chat_id):
        t_message = t_data['message']
        t_chat = t_message['chat']
        if not t_message['from']['is_bot']:
            if GroupProject.objects.filter(group_id=t_chat['id']).first() is None:
                code = uuid.uuid4()
                GroupCode.objects.create(group_id=t_chat['id'],
                                         code=code,
                                         group_name=t_chat['title'])
                self.send_message("Please, use this code {code}\
                 to bind this group with your project".format(code=code), chat_id)
            else:
                self.send_message("This group is already bound with a project", chat_id)


class TelegramProfilePlatform(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def post(request, *args, **kwargs):
        user = request.user
        code = request.data.get('code')
        profile_code = TelegramProfileCode.objects.filter(code=code)
        if profile_code.first() is None:
            return Response("Please, use valid code", status=status.HTTP_412_PRECONDITION_FAILED)
        profile_id = profile_code.first().profile_id
        if TelegramProfile.objects.filter(profile_id=profile_id).first() is not None \
                or TelegramProfile.objects.filter(user=user).first() is not None:
            return Response("Account or profile is already bound", status=status.HTTP_403_FORBIDDEN)
        TelegramProfile.objects.create(profile_id=profile_id, user=user, profile_name=profile_code.first().profile_name)
        profile_code.delete()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, *args, **kwargs):
        user = request.user

        if TelegramProfile.objects.filter(user=user).first() is None:
            return Response("Account is not bound")
        TelegramProfile.objects.filter(user=user).delete()
        return Response(status=status.HTTP_200_OK)


class GroupBindPlatform(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def post(request, *args, **kwargs):
        user = request.user
        code = request.data.get('code')
        project_id = kwargs.get("pk")
        project = Project.objects.filter(pk=project_id).first()
        group_code = GroupCode.objects.filter(code=code)
        if group_code.first() is None:
            return Response("Please, use valid code", status=status.HTTP_412_PRECONDITION_FAILED)
        group_id = group_code.first().group_id
        group_name = group_code.first().group_name
        if GroupProject.objects.filter(group_id=group_id).first() is not None \
                or GroupProject.objects.filter(project=project).first() is not None:
            return Response("Group or Project is already bound", status=status.HTTP_403_FORBIDDEN)
        if ProjectAndUser.objects.filter(project=project, user=user).first() is None:
            return Response("You are not member of this project", status=status.HTTP_403_FORBIDDEN)
        GroupProject.objects.create(group_id=group_id, project_id=project_id, group_name=group_name)
        group_code.delete()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, *args, **kwargs):
        user = request.user
        project_id = kwargs.get("pk")
        project = Project.objects.filter(pk=project_id).first()
        if ProjectAndUser.objects.filter(project=project, user=user).first() is None:
            return Response("You are not member of this project", status=status.HTTP_403_FORBIDDEN)
        if GroupProject.objects.filter(project=project).first() is None:
            return Response("Project is not bound")
        GroupProject.objects.filter(project=project).delete()
        return Response(status=status.HTTP_200_OK)
