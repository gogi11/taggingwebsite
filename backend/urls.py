from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views import UserViewSet, ElementViewSet, TagViewSet, MeViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"elements", ElementViewSet, basename="element")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"me", MeViewSet, basename="me")

urlpatterns = [
    path("", include(router.urls)),
]
