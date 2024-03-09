from django.db import models
from django.db.models import JSONField

class User(models.Model):
    username = models.CharField(max_length=255,unique=True)
    password = models.CharField(max_length=255)
    housekey = models.CharField(max_length=255)
    link_image = models.CharField(max_length=255)
    embedding_vector = JSONField()

class House(models.Model):
    housekey = models.CharField(max_length=255,unique=True)
    status = models.IntegerField()