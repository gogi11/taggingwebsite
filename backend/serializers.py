from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.models import Element, Tag, Tagging

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    to_delete = serializers.BooleanField(required=False)

    class Meta:
        model = Tag
        fields = ['name', 'to_delete']
        extra_kwargs = {
            'name': {'required': True, 'validators': []}
        }


class ElementSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Element
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def create(self, validated_data):
        request = self.context.get("request", None)
        user = request.user if request and request.user.is_authenticated else None
        tags_data = validated_data.pop("tags", None)
        element = Element.objects.create(user=user, **validated_data)
        if tags_data:
            for tag in tags_data:
                tags, created = Tag.objects.get_or_create(name=tag['name'])
                tp, created = Tagging.objects.get_or_create(elements=element, tags=tags)
                tp.save()
        return element

    def update(self, instance, validated_data):
        request = self.context.get("request", None)
        user = request.user if request and request.user.is_authenticated else None
        if not user or user.id == instance.id:
            tags_data = validated_data.pop("tags", None)
            if tags_data:
                for tag in tags_data:
                    if 'to_delete' in tag and tag['to_delete']:
                        tags = Tag.objects.filter(name=tag['name'])
                        if tags.count() == 1:
                            Tagging.objects.filter(tags=tags[0], elements=instance).delete()
                    else:
                        tags, created = Tag.objects.get_or_create(name=tag['name'])
                        tp, created = Tagging.objects.get_or_create(elements=instance, tags=tags)
                        tp.save()
            return super(ElementSerializer, self).update(instance, validated_data)
        raise ValidationError(detail="You don't have permission to update it!")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password', 'username']
        extra_kwargs = {
            'password': {'write_only': True}
        }

