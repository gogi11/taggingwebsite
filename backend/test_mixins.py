import json
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from backend.models import Element, Tag, Tagging


def set_credentials(client, username, password="Qwerty1234!"):
    response = client.post(
        reverse("rest_login"), data={"username": username, "password": password}
    )
    json_content = json.loads(response.content)
    client.credentials(HTTP_AUTHORIZATION="Token " + json_content.get("key"))


def get_user_and_client(username, password="Qwerty1234!", is_staff=False):
    user, exists = User.objects.get_or_create(username=username, is_staff=is_staff)
    user.set_password(password)
    user.save()
    client = APIClient()
    client.login(user=user, password=password)
    set_credentials(client, username, password)
    return user, client


class UserTestCase(TestCase):
    def setUp(self) -> None:
        super(UserTestCase, self).setUp()
        self.user, self.client = get_user_and_client("user1")
        self.userOther, self.clientOther = get_user_and_client("user2")
        self.admin, self.clientAdmin = get_user_and_client(username="admin", is_staff=True)
        self.clientUnauthenticated = APIClient()

    def assert_json_to_user(self, json, user):
        self.assertEqual(json["username"], user.username)
        self.assertEqual(json["id"], user.id)

    def assert_json_as_user(self, json):
        for user in User.objects.all():
            if json["username"] == user.username and json["id"] == user.id:
                return
        self.fail("That json is not of an existing user:\n"+str(json))


class ElementTestCase(UserTestCase):
    def setUp(self) -> None:
        super(ElementTestCase, self).setUp()
        self.data = {
            "description": "My fav film",
            "title": "Da Film Name",
            "tags": [
                {"name": "strange"},
                {"name": "wow"}
            ]
        }
        self.tag = Tag.objects.create(name="some tag")
        self.element = Element.objects.create(title="New element", user=self.user)
        Tagging.objects.create(tag=self.tag, element=self.element)
        self.assertEqual(Element.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 1)

    def assert_json_is_element(self, json, element):
        self.assertEqual(json["title"], element.title)
        self.assertEqual(json["description"], element.description)
        self.assertEqual(json["id"], element.id)
        self.assertEqual(len(json["tags"]), element.tags.count())
        for tag in json["tags"]:
            self.assertIsNotNone(element.tags.filter(name=tag["name"]).first())
