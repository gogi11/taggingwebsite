import django_filters
from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters, mixins
from rest_framework.authtoken.models import Token
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.models import Element, Tag
from backend.serializers import ElementSerializer, UserSerializer, TagSerializer

User = get_user_model()


class IsTheUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            (request.user and obj == request.user)
        )


class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or (request.user and request.user.is_authenticated)
        )


class MeViewSet(mixins.CreateModelMixin, GenericViewSet):
    def create(self, request, *args, **kwargs):
        token = get_object_or_404(Token.objects, key=request.data["key"])
        serializer = UserSerializer(token.user)
        return Response(serializer.data, 201)


class TagViewSet(viewsets.ViewSet):
    queryset = Tag.objects.all()

    def list(self, request):
        if self.queryset.count() > 0:
            paginator = LimitOffsetPagination()
            result_page = paginator.paginate_queryset(self.queryset, request)
            serializer = TagSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        return Response({})

    def retrieve(self, request, pk=None):
        tag = get_object_or_404(self.queryset, name=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)


class ElementViewSet(viewsets.ModelViewSet):
    queryset = Element.objects.all()
    serializer_class = ElementSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["tags__name", "user", "title"]
    search_fields = ['description', 'title']
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request, *args, **kwargs):
        limit = request.GET.get('limit', None)
        if limit and isinstance(limit, int):
            self.queryset = self.queryset.filter()[:limit]
        tags = request.GET.get('tags', None)
        or_operator = request.GET.get('or', False)
        if tags:
            tags = str(tags).split(",")
            if not or_operator:
                for tag in tags:
                    self.queryset = self.queryset.filter(tags__name=tag)
            else:
                self.queryset = self.queryset.filter(tags__name__in=tags).distinct()
        return super(ElementViewSet, self).list(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsTheUser]
    queryset = User.objects.all()
    #
    # def get_queryset(self):
    #     if self.request.user.is_staff:
    #         return User.objects.all()
    #     else:
    #         return User.objects.filter(pk=self.request.user.pk)



