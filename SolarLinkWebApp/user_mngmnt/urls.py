from django.urls import path, include
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path("register/", views.register, name="register"),
    path("product/", views.product, name="product"),
    path("data/", views.data, name="data")
]