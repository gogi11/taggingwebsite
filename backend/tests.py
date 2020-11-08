import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


def get_user_and_client(username, password="Qwerty1234!", is_staff=False):
    user = User.objects.create(username=username, is_staff=is_staff)
    user.set_password(password)
    user.save()
    client = APIClient()
    response = client.post(
        reverse("rest_login"), data={"username": username, "password": password}
    )
    json_content = json.loads(response.content)
    client.credentials(HTTP_AUTHORIZATION="Bearer " + json_content.get("key"))
    return user, client


class TestUserViewSet(TestCase):
    def setUp(self) -> None:
        super(TestUserViewSet, self).setUp()
        self.user, self.client = get_user_and_client("user1")
        self.userOther, self.clientOther = get_user_and_client("user2")
        self.admin, self.clientAdmin = get_user_and_client(username="admin", is_staff=True)
        self.clientUnauthenticated = APIClient()
        pass

    def test_get_all_users_doesnt_work_when_unauthenticated(self):
        response = self.clientUnauthenticated.get(reverse("user-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_get_all_users_doesnt_work_when_logged_in_as_normal_user(self):
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0].get("username"), self.user.username)

    def test_get_all_users_works_when_logged_in_as_admin(self):
        response = self.clientAdmin.get(reverse("user-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

    def test_get_user_detail_works_when_authenticated(self):
        response = self.client.get(reverse("user-detail", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 200)

    def test_get_user_detail_doesnt_work_when_you_try_to_get_other_user(self):
        response = self.clientOther.get(reverse("user-detail", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 404)

    def test_get_user_detail_doesnt_work_when_unauthenticated(self):
        response = self.clientUnauthenticated.get(reverse("user-detail", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 404)

# Create your tests here.
