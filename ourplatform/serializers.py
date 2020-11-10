from rest_framework import serializers
from .models import Project, Event, TelegramEvent, SlackEvent, GithubEvent


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['pk', 'name', 'team_lead', 'telegram_bonus', 'slack_bonus', 'git_bonus']


class EventSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(read_only=True, source="project.name")

    class Meta:
        model = Event
        fields = ('pk', 'timestamp', 'user', 'project_name')




class TelegramEventSerializer(EventSerializer):
    event_bonus  = serializers.CharField(read_only=True, source="project.telegram_bonus")
    event_type = serializers.CharField(read_only=True, default='Telegram')
    class Meta(EventSerializer.Meta):
        model = TelegramEvent
        fields = EventSerializer.Meta.fields+('message', 'chat', 'event_bonus', 'event_type')




class SlackEventSerializer(EventSerializer):
    event_bonus  = serializers.CharField(read_only=True, source="project.telegram_bonus")
    event_type = serializers.CharField(read_only=True, default='Slack')
    class Meta(EventSerializer.Meta):
        model = SlackEvent
        fields = ['message', 'channel', 'event_bonus', 'event_type']




class GitHubEventSerializer(EventSerializer):
    event_type = serializers.CharField(read_only=True, default='GitHub')
    event_bonus  = serializers.CharField(read_only=True, source="project.telegram_bonus")

    class Meta(EventSerializer.Meta):
        model = GithubEvent
        fields = EventSerializer.Meta.fields+ ('type', 'event_bonus', 'repo', 'metaData', 'event_type')


