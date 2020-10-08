from rest_framework import serializers
from .models import Question, Score, Topic


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'topic']


class QuestionSerializer(serializers.ModelSerializer):
    answer = serializers.CharField(max_length=1024, write_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question', 'topic', 'answer', 'hint']

class SupervisorQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question', 'topic', 'answer', 'hint']


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['user', 'topic', 'is_solved', 'question']
