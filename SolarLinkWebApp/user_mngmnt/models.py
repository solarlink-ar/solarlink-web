from django.db import models

# Create your models here.

class Data(models.Model):
    id_producto = models.EmailField(max_length=40, primary_key=True)
    email = models.EmailField()
    password = models.CharField(max_length=20)
    consumo_min = models.IntegerField()
    voltaje_min = models.IntegerField()
    corriente_min = models.IntegerField()
    fecha_hora_min = models.DateTimeField()