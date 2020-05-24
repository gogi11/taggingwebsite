import django_filters
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from backend.models import Element
from backend.serializers import ElementSerializer, UserSerializer

User = get_user_model()


class ElementViewSet(viewsets.ModelViewSet):
    queryset = Element.objects.all()
    serializer_class = ElementSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['artist__id']


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


