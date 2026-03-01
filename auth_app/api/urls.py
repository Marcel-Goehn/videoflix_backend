from django.urls import path
from .views import (RegistrationAPIView, AccountActivationView, LoginView, LogoutView,
                    RefreshView)

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("activate/<str:uidb64>/<str:token>/", AccountActivationView.as_view(), name="activate"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", RefreshView.as_view(), name="refresh")
]