from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views import UserViewSet, ElementViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"elements", ElementViewSet, basename="element")

urlpatterns = [
    path("", include(router.urls)),
]
