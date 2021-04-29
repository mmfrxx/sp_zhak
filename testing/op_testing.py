from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import User
from ourplatform.models import Project, ProjectAndUser


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

        self.login_response = self.client.login(
            username=self.new_user1.username, password=new_user1_data["password"])

        self.create_url = reverse('create_project')
        self.set_team_lead_url = reverse('set_team_lead')
        self.add_team_member_url = reverse('add_team_member')
        self.delete_team_member_url = reverse('remove_team_member')
        self.get_user_info = reverse('get-user-info', kwargs={"pk": 1})
        self.get_projects_for_user = reverse('get-projects-for-user', kwargs={"pk":1})

    def test_ProjectView_post(self):
        if self.login_response is True:
            create_url = reverse('create_project')
            data = {
                "name": "project",
                "telegram_bonus": 40,
                "slack_bonus": 30,
                "git_bonus": 20
            }
            response = self.client.post(create_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Project.objects.count(), 1)

    def test_Add_team_lead_post(self):
        if self.login_response is True:
            create_url = reverse('create_project')
            set_team_lead_url = reverse('set_team_lead')
            data = {
                "name": "project",
                "telegram_bonus": 40,
                "slack_bonus": 30,
                "git_bonus": 20
            }
            self.client.post(create_url, data, format='json')
            data = {
                "username": self.new_user1.username,
                "pk": 1
            }
            response = self.client.post(set_team_lead_url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Project.objects.filter(pk=1).first().team_lead.username, self.new_user1.username)

    def test_Delete_team_lead_delete(self):
        if self.login_response is True:
            url = reverse('create_project')
            set_team_lead_url = reverse('set_team_lead')
            delete_team_lead_url = reverse('delete_team_lead')
            data = {
                "name": "project",
                "telegram_bonus": 40,
                "slack_bonus": 30,
                "git_bonus": 20
            }
            self.client.post(url, data, format='json')
            data = {
                "username": self.new_user1.username,
                "pk": 1
            }
            self.client.post(set_team_lead_url, data, format="json")
            self.assertEqual(Project.objects.filter(pk=1).first().team_lead.username, self.new_user1.username)
            self.client.delete(delete_team_lead_url, data, format="json")
            self.assertEqual(Project.objects.filter(pk=1).first().team_lead, None)

    def test_Add_team_member_post(self):
        if self.login_response is True:
            data = {
                "name": "project",
                "telegram_bonus": 40,
                "slack_bonus": 30,
                "git_bonus": 20
            }
            self.client.post(self.create_url, data, format='json')
            data = {
                "username": self.new_user1.username,
                "pk": 1
            }
            self.client.post(self.add_team_member_url, data, format='json')
            self.assertEqual(ProjectAndUser.objects.filter(user__username=self.new_user1.username,
                                                           project_id=1).exists(), True)

    def test_Remove_team_member_delete(self):
        if self.login_response is True:
            data = {
                "name": "project",
                "telegram_bonus": 40,
                "slack_bonus": 30,
                "git_bonus": 20
            }
            self.client.post(self.create_url, data, format='json')
            data = {
                "username": self.new_user1.username,
                "pk": 1
            }
            self.client.post(self.add_team_member_url, data, format='json')
            self.assertEqual(ProjectAndUser.objects.filter(user__username=self.new_user1.username,
                                                           project_id=1).exists(), True)
            self.client.delete(self.delete_team_member_url, data, format='json')
            self.assertEqual(ProjectAndUser.objects.filter(user__username=self.new_user1.username,
                                                           project_id=1).exists(), False)

    def test_GetUserInfoView_get(self):
        if self.login_response:
            response = self.client.get(self.get_user_info)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.content_params), 7)

    def test_GetProjectsForUserView_get(self):
        if self.login_response:
            data = {
                "name": "project",
                "telegram_bonus": 40,
                "slack_bonus": 30,
                "git_bonus": 20
            }
            self.client.post(self.create_url, data, format="json")
    # def test1(self):
    #     self.assertEqual(1, 1)
    #
    # def test2(self):
    #     self.assertEqual(1, 1)
    #
    # def test3(self):
    #     self.assertEqual(1, 1)
    #
    # def test4(self):
    #     self.assertEqual(1, 1)
    #
    # def test5(self):
    #     self.assertEqual(1, 1)
    #
    # def test55(self):
    #     self.assertEqual(1, 1)
    #
    # def test6(self):
    #     self.assertEqual(1, 1)
    #
    # def test7(self):
    #     self.assertEqual(1, 1)
    #
    # def test8(self):
    #     self.assertEqual(1, 1)
    #
    # def test9(self):
    #     self.assertEqual(1, 1)
    #
    # def test10(self):
    #     self.assertEqual(1, 1)
    #
    # def test11(self):
    #     self.assertEqual(1, 1)
    #
    # def test12(self):
    #     self.assertEqual(1, 1)
    #
    # def test13(self):
    #     self.assertEqual(1, 1)
    #
    # def test14(self):
    #     self.assertEqual(1, 1)
    #
    # def test15(self):
    #     self.assertEqual(1, 1)
    #
    # def test16(self):
    #     self.assertEqual(1, 1)
    #
    # def test166(self):
    #     self.assertEqual(1, 1)
    #
    # def test1666(self):
    #     self.assertEqual(1, 1)
