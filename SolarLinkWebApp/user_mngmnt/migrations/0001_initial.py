# Generated by Django 4.2.1 on 2023-05-22 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id_producto', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=20)),
                ('consumo_min', models.IntegerField()),
                ('voltaje_min', models.IntegerField()),
                ('corriente_min', models.IntegerField()),
                ('fecha_hora_min', models.DateTimeField()),
            ],
        ),
    ]
