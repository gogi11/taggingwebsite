from django.urls import reverse
from backend.models import Element, Tag
from backend.test_mixins import UserTestCase, ElementTestCase
from rest_framework.authtoken.models import Token


class TestUserViewSet(UserTestCase):
    def test_get_all_users_works_when_unauthenticated(self):
        response = self.clientUnauthenticated.get(reverse("user-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 3)
        for i in range(3):
            self.assert_json_as_user(response.json()["results"][i])

    def test_get_all_users_works_when_logged_in_as_normal_user(self):
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 3)
        for i in range(3):
            self.assert_json_as_user(response.json()["results"][i])

    def test_get_all_users_works_when_logged_in_as_admin(self):
        response = self.clientAdmin.get(reverse("user-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 3)
        for i in range(3):
            self.assert_json_as_user(response.json()["results"][i])

    def test_get_user_detail_works_when_authenticated(self):
        response = self.client.get(reverse("user-detail", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assert_json_to_user(response.json(), self.user)

    def test_get_user_detail_works_to_get_other_user(self):
        response = self.clientOther.get(reverse("user-detail", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assert_json_to_user(response.json(), self.user)

    def test_get_user_detail_works_when_unauthenticated(self):
        response = self.clientUnauthenticated.get(reverse("user-detail", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assert_json_to_user(response.json(), self.user)


class TestCreateElement(ElementTestCase):
    def test_create_element_works_when_authenticated(self):
        response = self.client.post(reverse("element-list"), self.data, format="json")
        print(response.data)
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
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Element.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 1)


class TestUpdateElement(ElementTestCase):
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
        self.assertEqual(response.status_code, 401)
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


class TestListAndRetrieveElement(ElementTestCase):
    def test_list_element_works_when_unauthenticated(self):
        response = self.clientUnauthenticated.get(reverse("element-list"))
        self.assertEqual(response.status_code, 200)
        print(response.json())
        self.assertEqual(len(response.json()["results"]), 1)
        self.assert_json_is_element(response.json()["results"][0], self.element)

    def test_detail_element_works_when_unauthenticated(self):
        response = self.clientUnauthenticated.get(
            reverse("element-detail", kwargs={"pk": self.element.pk}),
        )
        self.assertEqual(response.status_code, 200)
        self.assert_json_is_element(response.json(), self.element)

    def test_list_element_filters(self):
        response = self.client.get(reverse("element-list") + "?tags="+self.tag.name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assert_json_is_element(response.json()["results"][0], self.element)


class TestTagViewSet(UserTestCase):
    def setUp(self) -> None:
        super(TestTagViewSet, self).setUp()
        self.nrOfTags = 10
        self.tags = [Tag.objects.create(name="Tag "+str(i)) for i in range(self.nrOfTags)]

    def test_post_doesnt_work(self):
        response = self.client.post(reverse("tags-list"), data={"pk":  "new tag"})
        self.assertEqual(response.status_code, 405)
        response = self.clientUnauthenticated.post(reverse("tags-list"), data={"name":  "new tag"})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Tag.objects.count(), self.nrOfTags)

    def test_delete_doesnt_work(self):
        response = self.client.post(reverse("tags-detail", kwargs={"pk": "Tag 1"}))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Tag.objects.count(), self.nrOfTags)

    def test_update_doesnt_work(self):
        response = self.client.patch(reverse("tags-detail", kwargs={"pk": "Tag 1"}),
                                     data={"name": "Tag "+str(self.nrOfTags+1)})
        self.assertEqual(response.status_code, 405)
        self.assertIsNotNone(Tag.objects.filter(name="Tag 1").first())
        self.assertIsNone(Tag.objects.filter(name="Tag "+str(self.nrOfTags+1)).first())

    def test_retrieve_doesnt_work(self):
        response = self.client.get(reverse("tags-detail", kwargs={"pk": "Tag 1"}))
        self.assertEqual(response.status_code, 200)

    def test_list_works(self):
        response = self.client.get(reverse("tags-list"))
        self.assertEqual(response.status_code, 200)
        print(response.json())
        self.assertEqual(len(response.json()["results"]), self.nrOfTags)
        for tag in response.json()["results"]:
            self.assertIsNotNone(Tag.objects.filter(name=tag["name"]).first())


class TestMeViewset(UserTestCase):
    def setUp(self) -> None:
        super(TestMeViewset, self).setUp()
        self.key = Token.objects.filter(user=self.user).first()

    def test_works_if_correct_token(self):
        response = self.client.post(reverse("me-list"), data={"key": self.key})
        self.assertEqual(response.status_code, 201)
        self.assert_json_to_user(response.json(), self.user)

    def test_doesnt_work_if_incorrect_token(self):
        response = self.clientUnauthenticated.post(reverse("me-list"), data={"key": "1"})
        self.assertEqual(response.status_code, 404)
