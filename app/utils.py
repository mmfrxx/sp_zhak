from django.core.checks import messages
from django.shortcuts import redirect
from rest_framework import request


def is_supervisor(user):
    if user.is_anonymous:
        return redirect('login')
    if not user.is_supervisor:
        messages.error(request, "Only supervisor can add a new question!")
        return redirect('/')
    return True