from django.contrib.auth import get_user_model
from rest_framework import serializers
from backend.models import Element
User = get_user_model()


class ElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Element
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password', 'username']
        extra_kwargs = {
            'password': {'write_only': True}
        }

