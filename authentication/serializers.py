from rest_framework import serializers
from django.contrib import auth
from .models import User
from rest_framework.exceptions import AuthenticationFailed


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)
    email = serializers.EmailField(max_length=255, min_length=5)
    username =serializers.CharField(max_length=255,min_length=3,read_only=True)
    tokens = serializers.CharField(max_length=68, min_length=6,read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'username', 'tokens']

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

        return {
            'email' : user.email,
            'username' : user.username,
            'tokens' : user.tokens
        }
        return super().validate(attrs)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=8,write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name']

    def validate(self, attrs):
        email = attrs.get('email','')
        username = attrs.get('username', '')
        first_name = attrs.get('first_name', '')
        last_name = attrs.get('last_name', '')
        
        if not username.isalnum():
            raise serializers.ValidationError('The username should contain only alphanumeric characters')
        if not first_name.isalnum() or not last_name.isalpha():
            raise serializers.ValidationError('The first or last name should contain only alphabetic characters')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': ('Username is already in use')})
        if User.objects.filter(email = email).exists():
            raise serializers.ValidationError({'email' : ('Email is already in use')})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

