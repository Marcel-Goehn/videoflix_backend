from django.urls import path
from .views import (RegistrationAPIView, AccountActivationView, LoginView, LogoutView,
                    RefreshView, PasswordResetView, NewPasswordView)

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("activate/<str:uidb64>/<str:token>/", AccountActivationView.as_view(), name="activate"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", RefreshView.as_view(), name="refresh"),
    path("password_reset/", PasswordResetView.as_view(), name="password-reset"),
    path("password_confirm/<str:uidb64>/<str:token>/", NewPasswordView.as_view(), name="new-password")
]