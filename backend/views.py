import django_filters
from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters
from rest_framework.permissions import BasePermission, SAFE_METHODS

from backend.models import Element
from backend.serializers import ElementSerializer, UserSerializer

User = get_user_model()


class IsUserOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user or request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        return bool(request.user and (obj == request.user or request.user.is_staff))


class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or (request.user and request.user.is_authenticated)
        )


class ElementViewSet(viewsets.ModelViewSet):
    queryset = Element.objects.all()
    serializer_class = ElementSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["tags__name", "user", "title"]
    search_fields = ['description', 'title']
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request, *args, **kwargs):
        tags = request.GET.get('tags', None)
        or_operator = request.GET.get('or', False)
        if tags:
            tags = str(tags).split(",")
            if not or_operator:
                for tag in tags:
                    self.queryset = Element.objects.filter(tags__name=tag)
            else:
                self.queryset = Element.objects.filter(tags__name__in=tags).distinct()
        return super(ElementViewSet, self).list(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsUserOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        else:
            return User.objects.filter(pk=self.request.user.pk)



