from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.generics import GenericAPIView

from django.contrib import messages
from django.shortcuts import redirect

from .serializers import TopicSerializer
from .models import Topic, Question, Score


class CreateTopicView(GenericAPIView):
    permission_classes = [IsAuthenticated,]
    
    def post(self, request):
        if request.user.is_anonymous:
            return redirect('login')
        if not request.user.is_supervisor:
            messages.error(request, "Only supervisor can add a new question!")
            return redirect('/')
        
        serializer = TopicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'id': serializer.data['id']}, status=HTTP_201_CREATED)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)


class UpdateTopicView(GenericAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        if request.user.is_anonymous:
            return redirect('login')
        if not request.user.is_supervisor:
            messages.error(request, "Only supervisor can add a new question!")
            return redirect('/')

        try:
            topic = Topic.objects.get(id=request.data["id"])
            topic.topic = request.data["new_topic"]
            topic.save()
            return Response({'Success': 'true'}, status=HTTP_201_CREATED)
        except Topic.DoesNotExist:
            return Response({'Success': 'failed'}, status=HTTP_404_NOT_FOUND)
        except:
            return Response({'Success': 'failed'}, status=HTTP_400_BAD_REQUEST)


class DeleteTopicView(GenericAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        if request.user.is_anonymous:
            return redirect('login')
        if not request.user.is_supervisor:
            messages.error(request, "Only supervisor can add a new question!")
            return redirect('/')

        try:
            topic = Topic.objects.get(id=request.data['id'])
            topic.delete()
            return Response({'Success': 'true'}, status=HTTP_200_OK)
        except Topic.DoesNotExist:
            return Response({'Success': 'failed'}, status=HTTP_404_NOT_FOUND)
        except:
            return Response({'Success': 'failed'}, status=HTTP_400_BAD_REQUEST)


class ReadTopicsView(GenericAPIView):
    def get_queryset(self):
        return

    def get(self, request):
        topics = [{"id": topic.id, "topic": topic.topic} for topic in Topic.objects.all()]
        return Response(topics, status=HTTP_200_OK)


class GetTopicNameView(GenericAPIView):
    def get_queryset(self):
        return

    def get(self, request):
        try:
            topic = Topic.objects.get(id=request.query_params['id'])
            return Response(TopicSerializer(topic).data, status=HTTP_200_OK)
        except Topic.DoesNotExist:
            return Response({'Success': 'failed'}, status=HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'Success': 'failed'}, status=HTTP_400_BAD_REQUEST)
