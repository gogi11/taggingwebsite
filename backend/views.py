import django_filters
from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters
from backend.models import Element
from backend.serializers import ElementSerializer, UserSerializer

User = get_user_model()


class ElementViewSet(viewsets.ModelViewSet):
    queryset = Element.objects.all()
    serializer_class = ElementSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["tags__name", "user", "title"]
    search_fields = ['description', 'title']
    
    def list(self, request, *args, **kwargs):
        tags = request.GET.get('tags', None)
        if tags:
            tags = str(tags).split(",")
            self.queryset = Element.objects.filter(tags__name__in=tags).distinct()
        return super(ElementViewSet, self).list(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


