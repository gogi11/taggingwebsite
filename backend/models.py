from django.db import models
from django.conf import settings


class Tag(models.Model):
    name = models.CharField(max_length=255)


class Element(models.Model):
    description = models.CharField(null=True, blank=True, max_length=10000)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="elements")
    title = models.CharField(null=True, blank=True, max_length=500)
    tags = models.ManyToManyField('Tag', through="Tagging")


class Tagging(models.Model):
    elements = models.ForeignKey('Element', on_delete=models.CASCADE)
    tags = models.ForeignKey('Tag', on_delete=models.CASCADE)
