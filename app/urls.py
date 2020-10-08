from django.urls import path
from .views import *
from .question_views import *
from .topic_views import *

urlpatterns = [
    path('generate-quiz', QuestionsByTopicView.as_view(), name='generate-quiz'),
    path('check-quiz', CheckQuizView.as_view(), name='check-quiz'),
    path('check-question', CheckQuestionView.as_view(), name='check-question'),
    path('load-leaderboard', LoadLeaderBoardView.as_view(), name='load-leaderboard'),
    path('get-user-scores', UserScoresView.as_view(), name='get-user-scores'),

    path('create-question', QuestionView.as_view()),
    path('get-questions-supervisor', QuestionView.as_view()),
    path('update-question', UpdateQuestionView.as_view(), name='update-question'),
    path('delete-question', DeleteQuestionView.as_view(), name='delete-question'),


    path('create-topic', CreateTopicView.as_view(), name='create-topic'),
    path('update-topic', UpdateTopicView.as_view(), name='update-topic'),
    path('delete-topic', DeleteTopicView.as_view(), name='delete-topic'),
    path('read-topics', ReadTopicsView.as_view(), name='read-topics'),
    path('get-topic-name', GetTopicNameView.as_view(), name='get-topic-name'),

    path('is-supervisor', IsSupervisorView.as_view(), name='is-supervisor')
]