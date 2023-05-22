from django.db import models

# Create your models here.

class Usuario(models.Model):
    id_prod=models.CharField(max_length=32)
    username=models.CharField(max_length=32)
    auth=models.BooleanField() #1 means token authenticated, 0 means not authenticated.

class totalPowerUsage(models.Model):
    totalPowerUsage=models.IntegerField()
    timestamp=models.DateField()

class solarPowerUsage(models.Model):
    solarPowerUsage=models.IntegerField()
    timestamp=models.DateField()

class providerPowerUsage(models.Model):
    providerPowerUsage=models.IntegerField()
    timestamp=models.DateField()

class batteryStatus(models.Model):
    batteryStatus=models.IntegerField()
    timestamp=models.DateField()