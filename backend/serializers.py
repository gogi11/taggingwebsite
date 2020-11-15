from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.models import Element, Tag, Tagging

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    to_delete = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Tag
        fields = ['name', 'to_delete']
        extra_kwargs = {
            'name': {'required': True, 'validators': []}
        }


class AbstractModelSerializer(serializers.ModelSerializer):
    def get_user_from_request(self):
        request = self.context.get("request", None)
        return request.user if request and request.user.is_authenticated else None


class ElementSerializer(AbstractModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Element
        fields = ["description", "user", "title", "tags", "id"]
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def create(self, validated_data):
        user = self.get_user_from_request()
        tags_data = validated_data.pop("tags", None)
        element = Element.objects.create(user=user, **validated_data)
        if tags_data:
            for tag in tags_data:
                tag_with_name, created = Tag.objects.get_or_create(name=tag['name'])
                tp, created = Tagging.objects.get_or_create(element=element, tag=tag_with_name)
                tp.save()
        return element

    def update(self, instance, validated_data):
        user = self.get_user_from_request()
        if not user or user.id == instance.id:
            tags_data = validated_data.pop("tags", None)
            if tags_data:
                for tag in tags_data:
                    if 'to_delete' in tag and tag['to_delete']:
                        tag_with_name = Tag.objects.filter(name=tag['name'])
                        if tag_with_name.count() == 1:
                            Tagging.objects.filter(tag=tag_with_name[0], element=instance).delete()
                    else:
                        tag_with_name, created = Tag.objects.get_or_create(name=tag['name'])
                        tp, created = Tagging.objects.get_or_create(element=instance, tag=tag_with_name)
                        tp.save()
            return super(ElementSerializer, self).update(instance, validated_data)
        raise ValidationError(detail="You don't have permission to update it!")


class UserSerializer(AbstractModelSerializer):
    tags = TagSerializer(required=False, many=True)

    class Meta:
        model = User
        fields = ['password', 'username', 'id', 'tags']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True, 'required': True},
            'username': {'required': True},
            'tags': {'read_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password")
        req_user = self.get_user_from_request()
        if req_user and req_user.id == instance.id:
            instance.set_password(password)
            instance.save()
            return super(UserSerializer, self).update(instance, validated_data)
        else:
            raise ValidationError(detail="You are trying to update another person's profile!")
