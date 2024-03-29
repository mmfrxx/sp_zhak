from rest_framework.generics import GenericAPIView
from .serializers import LoginSerializer, RegisterSerializer
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
# from django_email_verification import sendConfirm
from .models import User


# Create your views here.
class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer

    def check_user(self, user):
        email = user.get('email', '')
        username = user.get('username', '*&')
        first_name = user.get('first_name', '$%')
        last_name = user.get('last_name', '$#')
        password = user.get('password', '')

        if '@' in email:
            domen = email.split('@')[1]
        else:
            return (True, 'Email is invalid')

        if domen != "nu.edu.kz":
            return (True, "Use your nu.edu.kz email, please")

        if not username.isalnum():
            return (True,
                    'The username should contain only alphanumeric characters')
        if not first_name.isalpha() or not last_name.isalpha():
            return (True,
                    'The first or last name should contain only alphabetic characters')
        if User.objects.filter(username=username).exists():
            return (True,
                    'Username is already in use')
        if User.objects.filter(email=email).exists():
            return (True,
                    'Email is already in use')
        if len(password) < 8:
            return (True,
                    'Ensure password contains at least 8 symbols')
        return (False, '')

    def post(self, request):
        user = request.data
        check = self.check_user(user)
        if check[0]:
            return Response(check[1], status=HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=user)
        try:
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                user.is_active = True
                user_data = serializer.data
                user.save()
                # sendConfirm(user)
                return Response(user_data, status=HTTP_201_CREATED)
        except Exception:
            return Response("Please check your credentials", status=HTTP_400_BAD_REQUEST)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=HTTP_200_OK)
        except Exception:
            return Response('Invalid credentials', status=HTTP_406_NOT_ACCEPTABLE)


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