from rest_framework import serializers
from django.contrib import auth
from .models import User
from rest_framework.exceptions import AuthenticationFailed


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)
    email = serializers.EmailField(max_length=255, min_length=5)
    username = serializers.CharField(max_length=255, min_length=3, read_only=True)
    # tokens = serializers.CharField(max_length=68, min_length=6,read_only=True)
    refresh_token = serializers.SerializerMethodField('get_refresh_token')
    access_token = serializers.SerializerMethodField('get_access_token')

    class Meta:
        model = User
        fields = ['pk', 'email', 'password', 'username', 'refresh_token', 'access_token', 'is_admin',
                  'is_organizationOwner', 'is_marketplace_admin',
                  'is_manager'
                  ]
        read_only_fields = ['is_admin', 'is_organizationOwner', 'is_marketplace_admin',
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

        return {
            'pk': user.pk,
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens,
            'is_admin': user.is_admin,
            'is_organizationOwner': user.is_organizationOwner,
            'is_marketplace_admin': user.is_marketplace_admin,
            'is_manager': user.is_manager
        }
        return super().validate(attrs)


    def get_refresh_token(self, obj):
        tokens = obj['tokens']()
        return tokens['refresh']

    def get_access_token(self, obj):
        tokens = obj['tokens']()
        return tokens['access']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name']

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')
        first_name = attrs.get('first_name', '')
        last_name = attrs.get('last_name', '')

        if '@' in email:
            domen = email.split('@')[1]
        else:
            raise serializers.ValidationError('Email is invalid')

        if domen != "nu.edu.kz":
            raise serializers.ValidationError('Use your NU email.')

        if not username.isalnum():
            raise serializers.ValidationError('The username should contain only alphanumeric characters')
        if not first_name.isalnum() or not last_name.isalpha():
            raise serializers.ValidationError('The first or last name should contain only alphabetic characters')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': ('Username is already in use')})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': ('Email is already in use')})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'first_name', 'last_name', 'email', 'account_bonus']
