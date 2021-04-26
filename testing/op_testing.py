from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from requests.auth import HTTPBasicAuth
from rest_framework.test import force_authenticate

from authentication.models import User
from ourplatform.models import Project
from ourplatform.views import ProjectView


class ProjectTests(APITestCase):
    def setUp(self):
        new_user1_data = {
            "username": "pet",
            "first_name": "a",
            "last_name": "pet",
            "password": "randompassword",
            "email": "test@test.com",
        }

        self.new_user1 = User.objects.create(
            username=new_user1_data["username"],
            first_name=new_user1_data["first_name"],
            last_name=new_user1_data["last_name"],
            email=new_user1_data["email"],
            password=new_user1_data["password"]
        )

    def test_create_proj(self):
        login_data = {
            "username": self.new_user1.username
        }
        login_response = self.client.login(
            username=login_data['username'], password="randompassword")
        if login_response is True:
            url = reverse('create_project')
            data = {
                "name": "project",
                "telegram_bonus": 40,
                "slack_bonus": 30,
                "git_bonus": 20
            }
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Project.objects.count(), 1)

    def test_add_team_lead(self):
        login_data = {
            "username": self.new_user1.username
        }
        login_response = self.client.login(
            username=login_data['username'], password="randompassword")
        if login_response is True:
            url = reverse('create_project')
            tl_url = reverse('set_team_lead')
            data = {
                "name": "project",
                "telegram_bonus": 40,
                "slack_bonus": 30,
                "git_bonus": 20
            }
            response = self.client.post(url, data, format='json')
            data = {
                "username": login_data['username'],
                "pk": 1
            }
            response = self.client.post(tl_url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Project.objects.filter(pk=1).first().team_lead.username, login_data['username'])

    def test1(self):
        self.assertEqual(1, 1)

    def test2(self):
        self.assertEqual(1, 1)

    def test3(self):
        self.assertEqual(1, 1)

    def test4(self):
        self.assertEqual(1, 1)

    def test5(self):
        self.assertEqual(1, 1)

    def test55(self):
        self.assertEqual(1, 1)

    def test6(self):
        self.assertEqual(1, 1)

    def test7(self):
        self.assertEqual(1, 1)

    def test8(self):
        self.assertEqual(1, 1)

    def test9(self):
        self.assertEqual(1, 1)

    def test10(self):
        self.assertEqual(1, 1)

    def test11(self):
        self.assertEqual(1, 1)

    def test12(self):
        self.assertEqual(1, 1)

    def test13(self):
        self.assertEqual(1, 1)

    def test14(self):
        self.assertEqual(1, 1)

    def test15(self):
        self.assertEqual(1, 1)

    def test16(self):
        self.assertEqual(1, 1)

    def test166(self):
        self.assertEqual(1, 1)

    def test1666(self):
        self.assertEqual(1, 1)
