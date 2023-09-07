from django.urls import path, include
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path("signup/", views.signup, name="signup"),
    path("load-data/", views.load_data, name="load_data"),
    path("userpage/", views.userpage, name="userpage"),
    path("data", views.data, name="data"),
    path("index", views.index, name="index2"),
    path("creador", views.creador_datos, name="creador")
]