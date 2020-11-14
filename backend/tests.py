import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from backend.models import Element, Tag, Tagging


def get_user_and_client(username, password="Qwerty1234!", is_staff=False):
    user, exists = User.objects.get_or_create(username=username, is_staff=is_staff)
    user.set_password(password)
    user.save()
    client = APIClient()
    client.login(user=user, password=password)
    response = client.post(
        reverse("rest_login"), data={"username": username, "password": password}
    )
    json_content = json.loads(response.content)
    client.credentials(HTTP_AUTHORIZATION="Bearer " + json_content.get("key"))
    return user, client


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        super(BaseTestCase, self).setUp()
        self.user, self.client = get_user_and_client("user1")
        self.userOther, self.clientOther = get_user_and_client("user2")
        self.admin, self.clientAdmin = get_user_and_client(username="admin", is_staff=True)
        self.clientUnauthenticated = APIClient()


class TestUserViewSet(BaseTestCase):
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


class ElementViewSetTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(ElementViewSetTestCase, self).setUp()
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


class TestCreateElement(ElementViewSetTestCase):
    def test_create_element_works_when_authenticated(self):
        response = self.client.post(reverse("element-list"), self.data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(
            Element.objects.filter(title=self.data["title"]).get()
        )
        for tag in self.data["tags"]:
            self.assertIsNotNone(
                Tag.objects.filter(name=tag["name"]).get()
            )

    def test_create_element_doesnt_work_when_unauthenticated(self):
        response = self.clientUnauthenticated.post(reverse("element-list"), self.data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Element.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 1)


class TestUpdateElement(ElementViewSetTestCase):
    def test_update_element_works_when_authenticated(self):
        new_title = "new title"
        response = self.client.patch(
            reverse("element-detail", kwargs={"pk": self.element.pk}),
            data={"title": new_title},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Element.objects.count(), 1)
        self.assertEqual(Element.objects.get().title, new_title)

    def test_update_element_adds_tag_when_authenticated(self):
        new_tag = {"name": "new tag"}
        response = self.client.patch(
            reverse("element-detail", kwargs={"pk": self.element.pk}),
            data={"tags": [new_tag]},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Element.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 2)
        self.element.refresh_from_db()
        self.assertEqual(self.element.tags.count(), 2)
        for tag in self.element.tags.all():
            self.assertTrue(tag.name in [new_tag["name"], self.tag.name])

    def test_update_element_deletes_tag_when_authenticated(self):
        new_tag = {"name": self.tag.name, "to_delete": True}
        response = self.client.patch(
            reverse("element-detail", kwargs={"pk": self.element.pk}),
            data={"tags": [new_tag]},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Element.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 1)
        self.element.refresh_from_db()
        self.assertEqual(self.element.tags.count(), 0)

    def test_update_element_doesnt_work_when_unauthenticated(self):
        new_tag = {"name": "new tag"}
        response = self.clientUnauthenticated.patch(
            reverse("element-detail", kwargs={"pk": self.element.pk}),
            data={"tags": [new_tag]},
            format="json"
        )
        self.element.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Element.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(self.element.tags.count(), 1)

    def test_update_element_doesnt_work_when_other_user(self):
        new_tag = {"name": "new tag"}
        response = self.clientOther.patch(
            reverse("element-detail", kwargs={"pk": self.element.pk}),
            data={"tags": [new_tag]},
            format="json"
        )
        self.element.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Element.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(self.element.tags.count(), 1)


class TestListAndRetrieveElement(ElementViewSetTestCase):
    def test_list_element_works_when_unauthenticated(self):
        response = self.clientUnauthenticated.get(reverse("element-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["title"], self.element.title)

    def test_detail_element_works_when_unauthenticated(self):
        response = self.clientUnauthenticated.get(
            reverse("element-detail", kwargs={"pk": self.element.pk}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], self.element.title)

    def test_list_element_filters(self):
        response = self.client.get(reverse("element-list") + "?tags="+self.tag.name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["title"], self.element.title)

