from rest_framework import serializers
from django.contrib import auth
from .models import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST

class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68,
                                     min_length=8, write_only=True)
    email = serializers.EmailField(max_length=255, min_length=5)
    username = serializers.CharField(max_length=255,
                                     min_length=3, read_only=True)
    # tokens = serializers.CharField(max_length=68, min_length=6,read_only=True)
    refresh_token = serializers.CharField(max_length=68,
                                          min_length=6, read_only=True)
    access_token = serializers.CharField(max_length=68,
                                         min_length=6, read_only=True)

    class Meta:
        model = User
        fields = ['pk', 'email', 'password', 'username',
                  'refresh_token', 'access_token', 'is_admin',
                  'is_organizationOwner', 'is_marketplace_admin',
                  'is_manager']
        read_only_fields = ['is_admin', 'is_organizationOwner',
                            'is_marketplace_admin',
                            'is_manager']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials')
        if not user.is_active:
            raise AuthenticationFailed('Account is disabled')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')
        tokens = user.tokens()
        return {
            'pk': user.pk,
            'email': user.email,
            'username': user.username,
            'tokens': tokens,
            'is_admin': user.is_admin,
            'is_organizationOwner': user.is_organizationOwner,
            'is_marketplace_admin': user.is_marketplace_admin,
            'is_manager': user.is_manager,
            'access_token': tokens['access'],
            'refresh_token': tokens['refresh'],
        }



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=8,
                                     write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name']

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'first_name',
                  'last_name', 'email', 'account_bonus']




