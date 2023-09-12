from django.urls import path, include
from . import views

urlpatterns = [
    #auth
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path("signup/", views.signup, name="signup"),
    path("signup-verification/<token>", views.signup_verification, name="signup_verifiation"),
    # Info de usuario
    path("load-data/", views.load_data, name="load_data"),
    path("userpage/", views.userpage, name="userpage"),
    path("index", views.index, name="index2"),
    # tests
    path("creador", views.creador, name="creador"),
    path("sender", views.sender, name="sender")
]