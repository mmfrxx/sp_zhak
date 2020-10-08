from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.generics import GenericAPIView
from rest_framework.renderers import JSONRenderer

from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Count

from authentication.decorators import supervisor_required
from .serializers import QuestionSerializer, ScoreSerializer, SupervisorQuestionSerializer
from .models import Question, Score, Topic

import random
from operator import itemgetter
from .utils import is_supervisor


class QuestionView(GenericAPIView):
    permission_classes = [IsAuthenticated,]


    def get_queryset(self):
        return
    
    def post(self, request):
        if is_supervisor(request.user):
            serializer = QuestionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'Success': 'true'}, status=HTTP_201_CREATED)
            return Response(serializer.errors, HTTP_400_BAD_REQUEST)
        return Response(status=HTTP_401_UNAUTHORIZED)

    def get(self, request):
        if is_supervisor(request.user):
            try:
                topic = Topic.objects.get(topic=request.query_params['topic'])
                questions = [SupervisorQuestionSerializer(data) for data in topic.questions.order_by('id')]  
                return Response({'questions': [q.data for q in questions]}, status=HTTP_200_OK)
            except Topic.DoesNotExist:
                return Response({'Success': 'failed'}, status=HTTP_404_NOT_FOUND)
            except:
                return Response({'Success': 'failed'}, status=HTTP_400_BAD_REQUEST)
        return Response(status=HTTP_401_UNAUTHORIZED)


class UpdateQuestionView(GenericAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        if request.user.is_anonymous:
            return redirect('login')
        if not request.user.is_supervisor:
            messages.error(request, "Only supervisor can add a new question!")
            return redirect('/')

        try:
            question = Question.objects.get(id=request.data['id'])
            for attr in ["topic", "answer", "question", "hint"]:
                setattr(question, attr, request.data.get(attr, getattr(question, attr)))
            question.save()
            return Response({'Success': 'true'}, status=HTTP_201_CREATED)
        except Question.DoesNotExist:
            return Response({'Success': 'failed'}, status=HTTP_404_NOT_FOUND)
        except:
            return Response({'Success': 'failed'}, status=HTTP_400_BAD_REQUEST)


class DeleteQuestionView(GenericAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        if request.user.is_anonymous:
            return redirect('login')
        if not request.user.is_supervisor:
            messages.error(request, "Only supervisor can add a new question!")
            return redirect('/')

        try:
            question = Question.objects.get(id=request.data['id'])
            question.delete()
            return Response({'Success': 'true'}, status=HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({'Success': 'failed'}, status=HTTP_404_NOT_FOUND)
        except:
            return Response({'Success': 'failed'}, status=HTTP_400_BAD_REQUEST)


class QuestionsByTopicView(GenericAPIView):
    def get_queryset(self):
        return

    def get(self, request):
        try:
            topic = Topic.objects.get(topic=request.query_params['topic'])
            questions = [QuestionSerializer(data) for data in topic.questions.order_by('id')]
            return Response({
                'topic': request.query_params['topic'],
                'amount': len(questions),
                'questions': [q.data for q in questions]
            }, status=HTTP_200_OK)
        except Topic.DoesNotExist:
            return Response({'Success': 'failed'}, status=HTTP_404_NOT_FOUND)
        except:
            return Response({'Success': 'failed'}, status=HTTP_400_BAD_REQUEST)

