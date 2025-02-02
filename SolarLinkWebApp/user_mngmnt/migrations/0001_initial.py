# Generated by Django 4.2.5 on 2023-10-25 01:01

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Productos',
            fields=[
                ('product_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('conexion', models.GenericIPAddressField()),
            ],
        ),
        migrations.CreateModel(
            name='UsersTokens',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signup_token', models.CharField(default=None, max_length=300, null=True)),
                ('password_reset_token', models.CharField(default=None, max_length=300, null=True)),
                ('time', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TiempoReal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voltaje', models.IntegerField(default=None)),
                ('consumo_l1', models.IntegerField(default=None)),
                ('solar_l1', models.BooleanField(default=None)),
                ('consumo_l2', models.IntegerField(default=None)),
                ('solar_l2', models.BooleanField(default=None)),
                ('cargando', models.BooleanField(default=None, null=True)),
                ('voltaje_bateria', models.IntegerField(default=None, null=True)),
                ('errores', models.BooleanField(default=None, null=True)),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='isOnline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_online', models.BooleanField(default=None)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Emergencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voltaje', models.IntegerField(default=None)),
                ('consumo', models.IntegerField(default=None)),
                ('dia', models.IntegerField(default=None)),
                ('mes', models.IntegerField(default=None)),
                ('hora', models.IntegerField(default=None)),
                ('voltaje_bajo', models.BooleanField()),
                ('voltaje_alto', models.BooleanField()),
                ('red', models.BooleanField()),
                ('corriente', models.BooleanField()),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DatosHora',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voltaje_hora_red', models.IntegerField(default=None)),
                ('consumo_hora_solar', models.IntegerField(default=None)),
                ('consumo_hora_red', models.IntegerField(default=None)),
                ('consumo_l1_solar', models.IntegerField(default=None)),
                ('consumo_l1_proveedor', models.IntegerField(default=None)),
                ('consumo_l2_solar', models.IntegerField(default=None)),
                ('consumo_l2_proveedor', models.IntegerField(default=None)),
                ('hora', models.IntegerField(default=None)),
                ('dia', models.IntegerField(default=None)),
                ('mes', models.IntegerField(default=None)),
                ('año', models.IntegerField(default=None)),
                ('solar_ahora', models.BooleanField(default=None, null=True)),
                ('panel_potencia', models.IntegerField(default=None, null=True)),
                ('cargando', models.BooleanField(default=None, null=True)),
                ('voltaje_bateria', models.IntegerField(default=None, null=True)),
                ('errores', models.BooleanField(default=None, null=True)),
                ('product_id', models.CharField(max_length=50, null=True)),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user', 'año', 'mes', 'dia', 'hora'],
            },
        ),
        migrations.CreateModel(
            name='DatosDias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voltaje_maximo_dia_red', models.IntegerField(default=None)),
                ('voltaje_minimo_dia_red', models.IntegerField(default=None)),
                ('consumo_dia_red', models.IntegerField(default=None)),
                ('consumo_dia_solar', models.IntegerField(default=None)),
                ('dia', models.IntegerField(default=None)),
                ('mes', models.IntegerField(default=None)),
                ('año', models.IntegerField(default=None)),
                ('horas_potencia_panel', models.IntegerField(default=None, null=True)),
                ('potencia_dia_panel', models.IntegerField(default=None, null=True)),
                ('horas_de_carga', models.IntegerField(default=None, null=True)),
                ('voltajes_bateria', models.CharField(default=None, max_length=400, null=True)),
                ('errores', models.IntegerField(default=None, null=True)),
                ('product_id', models.CharField(default=None, max_length=50, null=True)),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user', 'año', 'mes', 'dia'],
            },
        ),
    ]
