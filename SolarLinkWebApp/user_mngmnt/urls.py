from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import path, include
from django.shortcuts import render, redirect
from . import views

# no permite acceder a las pestañas estando logueado
def unlogued_required(function, redirect_link):
    if function:
        def check(request):
            if request.user.username == '':
                return function(request)
            else:
                return redirect(redirect_link)
        return check

    else:
        def decorator(func):
            def check(request):
                if request.user.username == '':
                    return func(request)
                else:
                    return redirect(redirect_link)
            return check
        return decorator

urlpatterns = [
    # AUTH #
    # login
    path('login/', unlogued_required(views.Login.as_view(), redirect_link='index'), name='login'),
    path('logout/', views.logout, name='logout'),
    # signup
    path("signup/", unlogued_required(views.Signup.as_view(), redirect_link='index'), name="signup"),
    path("signup-verification/<token>/", views.SignupVerification.as_view(), name="signup_verification"),
    # password reset
    path("password-set/<token>", views.PasswordSet.as_view(), name="password_set"),
    path("password-set/", views.PasswordSet.as_view(), name="password_set"),
    path("password-reset/", views.PasswordReset.as_view(), name="password_reset"),
    # USER INFO #
    path("api-login/", csrf_exempt(views.APILogin.as_view()), name="api_login"),
    path("load-data/", csrf_exempt(views.LoadData.as_view()), name="load_data"),
    path("userpage/", login_required(views.UserPage.as_view()), name="userpage"),
    path("index/", views.index, name="index2"),
    # TESTS #
    path("creador/", views.creador, name="creador"),
    path("sender/", views.sender, name="sender"),
    path("confirmation/", views.confirmation, name="confirmation"),
    path("login-test", views.login_test, name="login2")
]