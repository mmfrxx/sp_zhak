from django.db import models

# Create your models here.
choices = (
    ('ethereum', 'ethereum'),
    ('mining', 'mining'),
    ('interactive', 'interactive'),
)


class Topic(models.Model):
    topic = models.CharField(max_length=256, unique=True)


class Question(models.Model):
    question = models.CharField(max_length=1024)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    answer = models.CharField(max_length=1024)
    hint = models.CharField(blank=True, null=True, max_length=1024)


class Score(models.Model):
    # user = models.ForeignKey(User, on_delete=)
    user = models.CharField(max_length=255)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    is_solved = models.BooleanField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

# class MultipleChoiceQuestion(models.Model):
#     question = models.CharField(max_length=1024)
#     topic = models.CharField(choices=choices, max_length=1024)
#     answer = models.CharField(max_length=1024)
#     hint = models.CharField(blank=True, null=True, max_length=1024)