from django.db import models

# Create your models here.

class Shop(models.Model):
    name = models.CharField(max_length=50)
    state = models.BooleanField()
    