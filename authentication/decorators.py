from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def supervisor_required(function):
    def _function(request,*args, **kwargs):
        if request.user.is_anonymous or not request.user.is_supervisor:
            if request.user.is_anonymous:
                return redirect('login')
            messages.error(request,"Only supervisor can add a new question!")
            return redirect('/')
        return function(request, *args, **kwargs)
    return _function