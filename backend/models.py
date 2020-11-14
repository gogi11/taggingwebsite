from django.db import models
from django.conf import settings


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Element(models.Model):
    description = models.CharField(null=True, blank=True, max_length=10000)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="elements", null=True)
    title = models.CharField(null=True, blank=True, max_length=500)
    tags = models.ManyToManyField('Tag', through="Tagging")


class Tagging(models.Model):
    element = models.ForeignKey('Element', on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
