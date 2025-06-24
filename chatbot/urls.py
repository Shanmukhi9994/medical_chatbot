from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("otp_verify/", views.otp_verify, name="otp_verify"),
    path("login/", views.user_login, name="login"),
   
    path("chatbot/", views.chatbot, name="chatbot"),  # ✅ Chatbot route
     path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]



