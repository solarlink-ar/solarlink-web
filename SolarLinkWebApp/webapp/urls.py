from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("que_somos", views.que_somos, name="que_somos"),
    path("contacto", views.contacto, name="contacto"),
    path("galeria", views.galeria, name="galeria"),
    path('datos', views.datos, name= 'datos')
]