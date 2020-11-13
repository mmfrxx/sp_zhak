from .serializers import GitHubEventSerializer, TelegramEventSerializer, SlackEventSerializer
from .models import GithubEvent, SlackEvent, TelegramEvent
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK


def serialize_events(events):

    data = []
    for event in events:
        if isinstance(event, TelegramEvent):
            event_data = TelegramEventSerializer(event).data
            data.append(event_data)
        if isinstance(event, SlackEvent):
            event_data = SlackEventSerializer(event).data
            data.append(event_data)
        if isinstance(event, GithubEvent):
            event_data = GitHubEventSerializer(event).data
            data.append(event_data)
    return Response(data, HTTP_200_OK)
