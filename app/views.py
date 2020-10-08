from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.generics import GenericAPIView
from rest_framework.renderers import JSONRenderer

from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Count

from authentication.decorators import supervisor_required
from .serializers import QuestionSerializer, ScoreSerializer
from .models import Question, Score, Topic

import random
from operator import itemgetter


class IsSupervisorView(GenericAPIView):
    def get(self, request):
        return Response({'is_supervisor': not request.user.is_anonymous and request.user.is_supervisor},
                        status=HTTP_200_OK)


class CheckQuestionView(GenericAPIView):
    serializer_class = ScoreSerializer
    def put(self, request):
        answer = request.data['answer']
        question = Question.objects.get(id=request.data['id'])
        score = question.answer.lower() == answer.lower()
        response = {
            "id": question.id,
            "question": question.question,
            "correct_answer": question.answer,
            "input": answer,
            "correct": score
        }

        if not request.user.is_anonymous and \
                not Score.objects.filter(question=question.id, user=request.user.username).exists():
            if score:
                serializer = ScoreSerializer(data={
                    "is_solved": True,
                    "question": question.id,
                    "topic": request.data["topic"],
                    "user": request.user.username
                })
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, HTTP_400_BAD_REQUEST)
            return Response(response, status=HTTP_201_CREATED)
        return Response(response, status=HTTP_200_OK)


class CheckQuizView(GenericAPIView):
    def put(self, request):
        answers = request.data["answers"]
        try:
            questions = [Question.objects.get(id=answer['id']) for answer in answers]
        except Question.DoesNotExist:
            return Response({'Success': 'failed'}, status=HTTP_404_NOT_FOUND)
        except:
            return Response({'Success': 'failed'}, status=HTTP_400_BAD_REQUEST)

        scores = [answer['answer'] == question.answer for answer, question in zip(answers, questions)]
        response = {
            "points": sum(scores),
            "total": len(scores),
            "answers": [
                {
                    "id": question.id,
                    "question": question.question,
                    "correct_answer": question.answer,
                    "input": answer['answer'],
                    "correct": score
                } for question, answer, score in zip(questions, answers, scores)]
        }
        if not request.user.is_anonymous:
            for question, score in zip(questions, scores):
                if score:
                    serializer = ScoreSerializer(data={
                        "is_solved": True,
                        "question": question.id,
                        "topic": question.topic,
                        "user": request.user.username
                    })
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response(serializer.errors, HTTP_400_BAD_REQUEST)
            return Response(response, status=HTTP_201_CREATED)
        return Response(response, status=HTTP_200_OK)


class UserScoresView(GenericAPIView):
    def get_queryset(self):
        return

    def get(self, request):
        topics = Topic.objects.all()
        totals = [len(Question.objects.filter(topic=topic.id)) for topic in topics]
        if not request.user.is_anonymous:
            user = request.user.username
            solved = [len(Score.objects.filter(topic=topic.id, user=user)) for topic in topics]
        else:
            solved = [0] * len(topics)
        response = [{
            "topic_id": topic.id,
            "topic_name": topic.topic,
            "total": total,
            "solved": solved_for_topic
        } for topic, total, solved_for_topic in zip(topics, totals, solved)]
        return Response(response, status=HTTP_200_OK)


class LoadLeaderBoardView(GenericAPIView):
    def get_queryset(self):
        return

    def get(self, request):
        leaders = Score.objects.values('user').annotate(sum=Count('is_solved'))
        leaders = [(x['user'], x['sum']) for x in leaders]
        leaders.sort(key=itemgetter(1), reverse=True)
        leaders = [{'place': place + 1, 'user': x[0], 'score': x[1]} for place, x in enumerate(leaders)]
        return Response({
            'leaderboard': leaders
        }, HTTP_200_OK)
