from django.urls import path

from . import views

urlpatterns = [
    # path home
    path("", views.index, name="index"),
    # path galeria
    path("galeria", views.galeria, name="galeria")
]