from django.urls import path, include
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path("register/", views.register, name="register"),
    path("product/", views.product, name="product"),
    path("load_data/", views.load_data, name="load_data"),
    path("userpage/", views.userpage, name="userpage")
]