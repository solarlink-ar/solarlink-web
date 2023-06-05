from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models


class Datos(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=50)

