from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from rest_framework_simplejwt.tokens import RefreshToken

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, username, email, first_name, last_name, password = None):
        if username is None:
            raise TypeError('Users should have a username')
        if email is None:
            raise TypeError('Users should have an Email')
        if first_name is None:
            raise TypeError('Users should have a first name')
        if last_name is None:
            raise TypeError('Users should have a last name')     


        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name
            )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, first_name, last_name, password = None):
        if password is None:
            raise TypeError('Password should not be null')
        
        user = self.create_user(username, email, first_name, last_name, password)
        user.is_superuser = True
        #user.is_staff = True
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255,unique=True,db_index=True)
    email = models.EmailField(max_length=255,unique=True,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    # is_staff = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255, unique=False, null=False)
    last_name = models.CharField(max_length=255, unique=False,null=False)
    is_organizationOwner = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_team_lead = models.BooleanField(default=False)
    is_marketplace_admin = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.username

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


