from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import LoginSerializer, RegisterSerializer
from rest_framework.response import Response
from rest_framework.status import *
from django.conf import settings
from django.contrib import auth
from rest_framework_simplejwt.authentication import JWTAuthentication
import datetime
from rest_framework.permissions import IsAuthenticated
import rest_framework_simplejwt
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django_email_verification import sendConfirm


# Create your views here.
class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data = serializer.data
        sendConfirm(user)
        return Response(user_data, status=HTTP_201_CREATED)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=HTTP_200_OK)


class LogoutView(GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=HTTP_400_BAD_REQUEST)